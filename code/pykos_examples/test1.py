from pykos import KOS # 导入PyKOS
import asyncio        # 导入asyncio异步库(PyKOS的远程调用基本都是通过异步IO实现的)


# 电机映射表
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
    "left_knee": 34,
    "left_ankle": 35,
    "right_hip_yaw": 41,
    "right_hip_roll": 42,
    "right_hip_pitch": 43,
    "right_knee": 44,
    "right_ankle": 45,
}



# 连接机器人(通过异步With语句是实现资源管理)
# 主函数必须使用async声明为异步函数，不然不能调用pykos的异步函数
# ip和port更改成机器人的网络地址，此处使用的是本地kos-sim的默认配置
async def main():
    async with KOS(ip='localhost', port=50051) as kos:
    # async with KOS(ip='192.168.42.1', port=50051) as kos: # 机器人端

        # 初始化电机
        for actuator_id in ACTUATOR_MAPPING.values():
            await kos.actuator.configure_actuator(
                actuator_id=actuator_id,
                torque_enabled=True,
            )
        # 将 13 号电机转动90度
        await kos.actuator.command_actuators([
            { 'actuator_id': 13, 'position': 90.0, "velocity": 100.0, "torque": 1.0 } # actuator_id为电机ID，position为目标位置(可选)，velocity为转速(可选)，torque为扭矩(可选)
        ])
        # 获取imu传感器值
        values = await kos.imu.get_imu_values()
        print(values)

# 通过asyncio.run异步调用主函数并阻塞
asyncio.run(main())