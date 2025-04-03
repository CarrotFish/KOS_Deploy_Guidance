# 简介
本文将通过官方示例介绍一些pyKOS的基本用法

[官方文档](https://kscalelabs.github.io/api-docs/pykos/actuator.html)

# 建立项目(以Visual Studio Code为例)
- 打开项目文件夹
- 新建main.py
- 将python环境调整为之前部署的Conda环境

# 构建示例项目(旋转指定电机并获取传感器值)
```python
from pykos import KOS # 导入PyKOS
import asyncio        # 导入asyncio异步库(PyKOS的远程调用基本都是通过异步IO实现的)

# 连接机器人(通过异步With语句是实现资源管理)
# ip和port更改成机器人的网络地址，此处使用的是本地kos-sim的默认配置
async with KOS(ip='localhost', port=50051) as kos:
  await kos.actuator.command_actuators([
    { 'actuator_id': 14, 'position': 90.0, "velocity": 100.0, "torque": 1.0 } # actuator_id为电机ID，position为目标位置(可选)，velocity为转速(可选)，torque为扭矩(可选)
  ])
  # 获取imu传感器值
  values = await kos.imu.get_imu_values()
  print(values)
```
