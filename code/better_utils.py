'''
Better Utils For PyKOS

由 CarrotFish1024 编写
'''

from pykos import KOS
from pykos.services.actuator import ActuatorCommand
import onnxruntime as ort
import numpy as np
import math
from typing import TypedDict
import time
import asyncio


ACTUATOR_MAPPING = {
    "left_shoulder_yaw": 11,
    "left_shoulder_pitch": 12,
    "left_elbow": 13,
    "right_shoulder_yaw": 21,
    "right_shoulder_pitch": 22,
    "right_elbow": 23,
    "left_hip_yaw": 31,
    "left_hip_roll": 32,
    "left_hip_pitch": 33,
    "left_knee_pitch": 34,
    "left_ankle_pitch": 35,
    "right_hip_yaw": 41,
    "right_hip_roll": 42,
    "right_hip_pitch": 43,
    "right_knee_pitch": 44,
    "right_ankle_pitch": 45,
}
MODEL_MAP = (
                ACTUATOR_MAPPING['right_hip_pitch'],
                ACTUATOR_MAPPING['left_hip_pitch'],
                ACTUATOR_MAPPING['right_hip_yaw'],
                ACTUATOR_MAPPING['left_hip_yaw'],
                ACTUATOR_MAPPING['right_hip_roll'],
                ACTUATOR_MAPPING['left_hip_roll'],
                ACTUATOR_MAPPING['right_knee_pitch'],
                ACTUATOR_MAPPING['left_knee_pitch'],
                ACTUATOR_MAPPING['right_ankle_pitch'],
                ACTUATOR_MAPPING['left_ankle_pitch']
            )

def transform_position(position:float)->float:
    position = position % 360
    if position > 180:
        position = position - 360
    return position

class BetterKOS(KOS):
    '''
        继承自KOS类，添加了command_actuators方法，添加了手动reset功能
        使用时可以无需configure电机和调用init方法，直接使用async with就行
        内置ONNX模型推理功能和姿态记忆功能
        eg:
        async with BetterKOS('192.168.1.100') as kos:
            await kos.command_actuators()
    '''
    source_positions = {}
    last_actions = np.zeros(10)
    last_time_second = -1
    phase: float = 0         # 步调相位/2pi
    walk_speed: float = 0.1    # 步态速度 1.0=2pi/s
    move_commands = np.zeros(3)  # 移动控制[x, y, z]
    session: ort.InferenceSession
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    async def init(self):
        # 初始化电机
        print('正在配置电机...')
        for actuator_id in ACTUATOR_MAPPING.values():
            await self.actuator.configure_actuator(
                actuator_id=actuator_id,
                torque_enabled=True,
                kp=20.0,
                kd=0.5
            )
        print('正在初始化电机位置，请注意，当前电机位置会被设置为0')
        states = await self.actuator.get_actuators_state(list(ACTUATOR_MAPPING.values()))
        for state in states.states:
            print(state)
            self.source_positions[state.actuator_id] = state.position
        print('电机位置初始化完成')
    async def move(self, actuator_id, position, speed=10):
        return await self.actuator.command_actuators([{
            'actuator_id': actuator_id,
            'position': transform_position(position + self.source_positions[actuator_id]),
            'velocity': speed
        }])
    async def command_actuators(self, commands:list[ActuatorCommand]):
        k = 1 if commands[0]['actuator_id']//10 == 4 else -1
        return await self.actuator.command_actuators([
            {
                'actuator_id': command['actuator_id'],
                'position': transform_position(command['position']*k + self.source_positions[command['actuator_id']]),
                'velocity': command.get('velocity', 20),
                'torque': command.get('torque', 0.1)
            }
            for command in commands
        ])
    async def __aenter__(self):
        await super().__aenter__()
        await self.init()
        return self
    
    async def load_session(self, session_path:str):
        self.session = ort.InferenceSession(session_path)
        print('ONNX模型加载成功')

    async def update(self):
        # 帧更新
        # 调整步态
        current_time_second = time.time()
        if self.last_time_second > 0:
            dt = current_time_second - self.last_time_second
            self.phase += self.walk_speed * dt
            if self.phase > 2*math.pi:
                self.phase -= 2*math.pi
        self.last_time_second = current_time_second
        # 获取传感器数据
        imu_euler_angles = await self.imu.get_euler_angles()
        imu_data = await self.imu.get_imu_values()
        imu_advanced_data = await self.imu.get_imu_advanced_values()
        base_ang_vel = [imu_data.gyro_x/180*math.pi, imu_data.gyro_y/180*math.pi, imu_data.gyro_z/180*math.pi]
        base_euler = [imu_euler_angles.roll/180*math.pi, imu_euler_angles.pitch/180*math.pi, imu_euler_angles.yaw/180*math.pi]
        # 获取关节位置和速度
        states = await self.actuator.get_actuators_state([
            ACTUATOR_MAPPING['right_hip_pitch'],
            ACTUATOR_MAPPING['left_hip_pitch'],
            ACTUATOR_MAPPING['right_hip_yaw'],
            ACTUATOR_MAPPING['left_hip_yaw'],
            ACTUATOR_MAPPING['right_hip_roll'],
            ACTUATOR_MAPPING['left_hip_roll'],
            ACTUATOR_MAPPING['right_knee_pitch'],
            ACTUATOR_MAPPING['left_knee_pitch'],
            ACTUATOR_MAPPING['right_ankle_pitch'],
            ACTUATOR_MAPPING['left_ankle_pitch']
        ])
        dof_pos = np.zeros(10)
        dof_vel = np.zeros(10)
        for state in states.states:
            k = 1 if state.actuator_id//10 == 4 else -1
            dof_pos[MODEL_MAP.index(state.actuator_id)] = k*(state.position - self.source_positions[state.actuator_id])/180*math.pi
            dof_vel[MODEL_MAP.index(state.actuator_id)] = k*state.velocity/180*math.pi
        # 推理
        next_actions = onnx_inference(self.session, self.phase, self.move_commands, {
            'ang_vel': 1.0,
            'dof_pos': 1.0,
            'dof_vel': 0.05,
            'lin_vel': 2.0,
            'quat': 1.0
        }, dof_pos, dof_vel, self.last_actions, base_ang_vel, base_euler, np.zeros(10))
        # 叠加增量
        self.last_actions = next_actions
        # 移动电机
        await self.command_actuators([{
            'actuator_id': MODEL_MAP[i],
            'position': (dof_pos[i] + next_actions[i])*180/math.pi
        } for i in range(10)])
    
    async def loop(self, delta_time:float=0.05):
        # 命令循环
        while True:
            await self.update()
            await asyncio.sleep(delta_time)
    




# ONNX 相关

class OBS_Scales(TypedDict):
    lin_vel: float
    ang_vel: float
    dof_pos: float
    dof_vel: float
    quat: float


def onnx_inference(session:ort.InferenceSession, phase:float, commands:np.ndarray, obs_scales: OBS_Scales, dof_pos: np.ndarray, dof_vel: np.ndarray, actions: np.ndarray, base_ang_vel: np.ndarray, base_euler: np.ndarray, default_dof_pos: np.ndarray):
    '''
        1. 输入：
            session: 已加载的onnx模型
            phase: 步态相位/2PI
            commands: 步态指令，[X方向线速度，Y方向线速度，Yaw方向角速度]
            obs_scales: 观测值缩放参数
            dof_pos: 关节位置(10)
            dof_vel: 关节速度(10)
            actions: 上一步动作(10)
            base_ang_vel: 角速度 [x, y, z]
            base_euler: 姿态欧拉角 [roll, pitch, yaw]
            default_dof_pos: 默认关节位置(10)
        2. 输出
            0   right_hip_pitch
            1   left_hip_pitch
            2   right_hip_yaw
            3   left_hip_yaw
            4   right_hip_roll
            5   left_hip_roll
            6   right_knee_pitch
            7   left_knee_pitch
            8   right_ankle_pitch
            9   left_ankle_pitch
            10  RESERVED
            11  RESERVED
    '''
    obs = np.zeros(45).astype(np.float32)
    obs[0] = math.sin(2*math.pi*phase)     # 步态周期的正弦值
    obs[1] = math.cos(2*math.pi*phase)     # 步态周期的余弦值
    obs[2] = commands[0] * obs_scales["lin_vel"]  # X方向线速度命令
    obs[3] = commands[1] * obs_scales["lin_vel"]  # Y方向线速度命令
    obs[4] = commands[2] * obs_scales["ang_vel"]  # Yaw方向角速度命令
    # 6-15: 关节位置 (10维)
    obs[5] = (dof_pos[0] - default_dof_pos[0]) * obs_scales["dof_pos"]  # right_hip_pitch
    obs[6] = (dof_pos[1] - default_dof_pos[1]) * obs_scales["dof_pos"]  # left_hip_pitch
    obs[7] = (dof_pos[2] - default_dof_pos[2]) * obs_scales["dof_pos"]  # right_hip_yaw
    obs[8] = (dof_pos[3] - default_dof_pos[3]) * obs_scales["dof_pos"]  # left_hip_yaw
    obs[9] = (dof_pos[4] - default_dof_pos[4]) * obs_scales["dof_pos"]  # right_hip_roll
    obs[10] = (dof_pos[5] - default_dof_pos[5]) * obs_scales["dof_pos"] # left_hip_roll
    obs[11] = (dof_pos[6] - default_dof_pos[6]) * obs_scales["dof_pos"] # right_knee_pitch
    obs[12] = (dof_pos[7] - default_dof_pos[7]) * obs_scales["dof_pos"] # left_knee_pitch
    obs[13] = (dof_pos[8] - default_dof_pos[8]) * obs_scales["dof_pos"] # right_ankle_pitch
    obs[14] = (dof_pos[9] - default_dof_pos[9]) * obs_scales["dof_pos"] # left_ankle_pitch
    # 16-25: 关节速度 (10维)
    obs[15] = dof_vel[0] * obs_scales["dof_vel"]  # right_hip_pitch 速度
    obs[16] = dof_vel[1] * obs_scales["dof_vel"]  # left_hip_pitch 速度
    obs[17] = dof_vel[2] * obs_scales["dof_vel"]  # right_hip_yaw 速度
    obs[18] = dof_vel[3] * obs_scales["dof_vel"]  # left_hip_yaw 速度
    obs[19] = dof_vel[4] * obs_scales["dof_vel"]  # right_hip_roll 速度
    obs[20] = dof_vel[5] * obs_scales["dof_vel"]  # left_hip_roll 速度
    obs[21] = dof_vel[6] * obs_scales["dof_vel"]  # right_knee_pitch 速度
    obs[22] = dof_vel[7] * obs_scales["dof_vel"]  # left_knee_pitch 速度
    obs[23] = dof_vel[8] * obs_scales["dof_vel"]  # right_ankle_pitch 速度
    obs[24] = dof_vel[9] * obs_scales["dof_vel"]  # left_ankle_pitch 速度
    # 26-35: 上一步动作 (10维)
    obs[25] = actions[0]  # right_hip_pitch 动作
    obs[26] = actions[1]  # left_hip_pitch 动作
    obs[27] = actions[2]  # right_hip_yaw 动作
    obs[28] = actions[3]  # left_hip_yaw 动作
    obs[29] = actions[4]  # right_hip_roll 动作
    obs[30] = actions[5]  # left_hip_roll 动作
    obs[31] = actions[6]  # right_knee_pitch 动作
    obs[32] = actions[7]  # left_knee_pitch 动作
    obs[33] = actions[8]  # right_ankle_pitch 动作
    obs[34] = actions[9]  # left_ankle_pitch 动作
    # 36-38: 角速度 (3维)
    obs[35] = base_ang_vel[0] * obs_scales["ang_vel"]  # X轴角速度
    obs[36] = base_ang_vel[1] * obs_scales["ang_vel"]  # Y轴角速度
    obs[37] = base_ang_vel[2] * obs_scales["ang_vel"]  # Z轴角速度
    # 39-41: 姿态欧拉角 (3维)
    obs[38] = base_euler[0] * obs_scales["quat"]  # Roll角（横滚）
    obs[39] = base_euler[1] * obs_scales["quat"]  # Pitch角（俯仰）
    obs[40] = base_euler[2] * obs_scales["quat"]  # Yaw角（偏航）
    # Reserved for future use(4)
    print('[Inference Input]', obs)
    # 执行推理
    results = session.run(None, {'obs': [obs]})[0][0]
    print('[Inference Output]', results)
    return results