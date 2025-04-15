"""Run reinforcement learning on the robot simulator."""

import argparse
import asyncio
import logging
import math
import time
from dataclasses import dataclass
from pathlib import Path

import colorlogging
import numpy as np
import onnxruntime as ort
from pykos import KOS
from scipy.spatial.transform import Rotation as R

logger = logging.getLogger(__name__)
# 设置一个日志记录器，用于日志输出，__name__表示当前模块的名字


@dataclass
class Actuator:
    actuator_id: int
    nn_id: int
    kp: float
    kd: float
    max_torque: float
    joint_name: str
"""
这是一个数据类，表示机器人中的一个执行器（例如，机器人关节的电动机）具体参数：
actuator_id: 执行器的ID
nn_id: 神经网络中的ID
kp: 比例增益
kd: 微分增益
max_torque: 最大扭矩
joint_name: 执行器对应的关节名称
"""

# ACTUATOR_LIST 是一个包含多个 Actuator 实例的列表，表示机器人不同关节的执行器
# 映射关系已经对应实机进行修改
# 本控制代码是行走的控制，故上肢锁定
ACTUATOR_LIST: list[Actuator] = [
    Actuator(actuator_id=31, nn_id=0, kp=300.0, kd=5.0, max_torque=40.0, joint_name="left_hip_pitch_04"),
    Actuator(actuator_id=32, nn_id=1, kp=120.0, kd=5.0, max_torque=30.0, joint_name="left_hip_roll_03"),
    Actuator(actuator_id=33, nn_id=2, kp=120.0, kd=5.0, max_torque=30.0, joint_name="left_hip_yaw_03"),
    Actuator(actuator_id=34, nn_id=3, kp=300.0, kd=5.0, max_torque=40.0, joint_name="left_knee_04"),
    Actuator(actuator_id=35, nn_id=4, kp=40.0, kd=5.0, max_torque=10.0, joint_name="left_ankle_02"),
    Actuator(actuator_id=41, nn_id=5, kp=300.0, kd=5.0, max_torque=40.0, joint_name="right_hip_pitch_04"),
    Actuator(actuator_id=42, nn_id=6, kp=120.0, kd=5.0, max_torque=30.0, joint_name="right_hip_roll_03"),
    Actuator(actuator_id=43, nn_id=7, kp=120.0, kd=5.0, max_torque=30.0, joint_name="right_hip_yaw_03"),
    Actuator(actuator_id=44, nn_id=8, kp=300.0, kd=5.0, max_torque=40.0, joint_name="right_knee_04"),
    Actuator(actuator_id=45, nn_id=9, kp=40.0, kd=5.0, max_torque=10.0, joint_name="right_ankle_02"),
    # Actuator(actuator_id=11, nn_id=10, kp=..., kd=..., max_torque=..., joint_name="left_shoulder_yaw"),
    # Actuator(actuator_id=12, nn_id=11, kp=..., kd=..., max_torque=..., joint_name="left_shoulder_pitch"),
    # Actuator(actuator_id=13, nn_id=12, kp=..., kd=..., max_torque=..., joint_name="left_elbow"),
    # Actuator(actuator_id=21, nn_id=13, kp=..., kd=..., max_torque=..., joint_name="right_shoulder_yaw"),
    # Actuator(actuator_id=22, nn_id=14, kp=..., kd=..., max_torque=..., joint_name="right_shoulder_pitch"),
    # Actuator(actuator_id=23, nn_id=15, kp=..., kd=..., max_torque=..., joint_name="right_elbow"),

]
# 将执行器ID映射到对应的神经网络ID。这个字典方便后续将执行器的动作与神经网络的输出进行对应
ACTUATOR_ID_TO_POLICY_IDX = {actuator.actuator_id: actuator.nn_id for actuator in ACTUATOR_LIST}

# 提取出所有执行器的ID，生成一个列表
ACTUATOR_IDS = [actuator.actuator_id for actuator in ACTUATOR_LIST]

"""
这是一个异步函数，模拟机器人行走的过程。参数：
model_path: ONNX模型文件的路径
default_position: 机器人的默认关节位置
host: 连接的主机地址
port: 连接的端口
num_seconds: 模拟运行的时长
"""
async def simple_walking(
    model_path: str | Path,
    default_position: list[float],
    host: str,
    port: int,
    num_seconds: float | None = 10.0,
) -> None:
    """Runs a simple walking policy.

    Args:
        model_path: The path to the ONNX model.
        default_position: The default joint positions for the legs.
        host: The host to connect to.
        port: The port to connect to.
        num_seconds: The number of seconds to run the policy for.
    """
    assert len(default_position) == len(ACTUATOR_LIST)

# 检查指定的模型文件是否存在，如果不存在，则抛出
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

# 使用ONNX Runtime加载并创建一个会话，用于推理
    session = ort.InferenceSession(model_path)

# 获取模型输出的详细信息
    output_details = [{"name": x.name, "shape": x.shape, "type": x.type} for x in session.get_outputs()]

# 接受输入数据并通过ONNX模型运行推理，返回输出
    def policy(input_data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        results = session.run(None, input_data)
        return {output_details[i]["name"]: results[i] for i in range(len(output_details))}

# 之后的部分即为配置执行器（电机）和仿真运行
    # 通过 KOS 与模拟器建立连接，并配置每个执行器的参数
    async with KOS(ip=host, port=port) as sim_kos:
        for actuator in ACTUATOR_LIST:
            await sim_kos.actuator.configure_actuator(
                actuator_id=actuator.actuator_id,
                kp=actuator.kp,
                kd=actuator.kd,
                max_torque=actuator.max_torque,
                torque_enabled=True,
            )

        try:
            # 设置初始位姿
            await sim_kos.sim.reset(
                pos={"x": 0.0, "y": 0.0, "z": 1.05},
                quat={"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                joints=[
                    {
                        "name": actuator.joint_name,
                        "pos": pos,
                    }
                    for actuator, pos in zip(ACTUATOR_LIST, default_position)
                ],
            )
        except Exception:
            logger.warning("Failed to reset simulation")

        start_time = time.time()
        end_time = None if num_seconds is None else start_time + num_seconds

        default = np.array(default_position)
        target_q = np.zeros(10, dtype=np.double)
        prev_actions = np.zeros(10, dtype=np.double)
        hist_obs = np.zeros(570, dtype=np.double)

        input_data = {
            "x_vel.1": np.zeros(1).astype(np.float32),
            "y_vel.1": np.zeros(1).astype(np.float32),
            "rot.1": np.zeros(1).astype(np.float32),
            "t.1": np.zeros(1).astype(np.float32),
            "dof_pos.1": np.zeros(10).astype(np.float32),
            "dof_vel.1": np.zeros(10).astype(np.float32),
            "prev_actions.1": np.zeros(10).astype(np.float32),
            "projected_gravity.1": np.zeros(3).astype(np.float32),
            "buffer.1": np.zeros(570).astype(np.float32),
    }

        x_vel_cmd = 1.0
        y_vel_cmd = 0.0
        yaw_vel_cmd = 0.0
        frequency = 50

        start_time = time.time()
        next_time = start_time + 1 / frequency

        while end_time is None or time.time() < end_time:
            # 获取执行器的状态和IMU（惯性测量单元）的四元数
            response, raw_quat = await asyncio.gather(
                sim_kos.actuator.get_actuators_state(ACTUATOR_IDS),
                sim_kos.imu.get_quaternion(),
            )
            # 将执行器的角度转换为弧度，获取IMU的旋转四元数并转换为旋转矩阵
            positions = np.array([math.radians(state.position) for state in response.states])
            velocities = np.array([math.radians(state.velocity) for state in response.states])
            r = R.from_quat([raw_quat.x, raw_quat.y, raw_quat.z, raw_quat.w])

            gvec = r.apply(np.array([0.0, 0.0, -1.0]), inverse=True).astype(np.double)

            # Need to apply a transformation from the IMU frame to the frame
            # that we used to train the original model.
            gvec[0] = -gvec[0]
            gvec[1] = -gvec[1]
            # 构造输入数据，包含机器人的当前速度、角速度、关节位置等信息
            cur_pos_obs = positions - default
            cur_vel_obs = velocities
            input_data["x_vel.1"] = np.array([x_vel_cmd], dtype=np.float32)
            input_data["y_vel.1"] = np.array([y_vel_cmd], dtype=np.float32)
            input_data["rot.1"] = np.array([yaw_vel_cmd], dtype=np.float32)
            input_data["t.1"] = np.array([time.time() - start_time], dtype=np.float32)
            input_data["dof_pos.1"] = cur_pos_obs.astype(np.float32)
            input_data["dof_vel.1"] = cur_vel_obs.astype(np.float32)
            input_data["prev_actions.1"] = prev_actions.astype(np.float32)
            input_data["projected_gravity.1"] = gvec.astype(np.float32)
            input_data["buffer.1"] = hist_obs.astype(np.float32)

            # 推理当前的动作
            policy_output = policy(input_data)
            positions = policy_output["actions_scaled"]
            curr_actions = policy_output["actions"]
            hist_obs = policy_output["x.3"]
            prev_actions = curr_actions

            target_q = positions + default
            
            # 根据推理结果计算目标位置，并将目标位置转换为角度，生成命令发送给执行器
            commands = []
            for actuator_id in ACTUATOR_IDS:
                policy_idx = ACTUATOR_ID_TO_POLICY_IDX[actuator_id]
                raw_value = target_q[policy_idx]
                command_deg = raw_value
                command_deg = math.degrees(raw_value)
                commands.append({"actuator_id": actuator_id, "position": command_deg})

            # 根据频率控制模拟器更新的时间间隔
            await sim_kos.actuator.command_actuators(commands)
            await asyncio.sleep(max(0, next_time - time.time()))
            next_time += 1 / frequency


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--num-seconds", type=float, default=None)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    colorlogging.configure(level=logging.DEBUG if args.debug else logging.INFO)

    model_path = Path(__file__).parent / "simple_walking.onnx"

    # Defines the default joint positions for the legs.
    default_position = [0.23, 0.0, 0.0, 0.441, -0.195, -0.23, 0.0, 0.0, -0.441, 0.195]
    await simple_walking(model_path, default_position, args.host, args.port, args.num_seconds)


if __name__ == "__main__":
    asyncio.run(main())