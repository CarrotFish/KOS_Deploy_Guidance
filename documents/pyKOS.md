# 简介
本文将通过官方示例介绍一些pyKOS的基本用法
能够调用的函数主要看 ***xxxServiceClient*** 部分

[官方文档(actuator)](https://kscalelabs.github.io/api-docs/pykos/actuator.html)
[官方文档(imu)](https://kscalelabs.github.io/api-docs/pykos/imu.html)
[官方文档(sound)](https://kscalelabs.github.io/api-docs/pykos/sound.html)
[官方文档(LED Matrix)](https://kscalelabs.github.io/api-docs/pykos/led_matrix.html)
[官方文档(Inference)](https://kscalelabs.github.io/api-docs/pykos/inference.html)
[官方文档(Process Manager)](https://kscalelabs.github.io/api-docs/pykos/process_manager.html)

# 建立项目(以Visual Studio Code为例)
- 打开项目文件夹
- 新建main.py
- 将python环境调整为之前部署的Conda环境

# 编写PyKOS程序的主要流程
- 导入KOS类
- 初始化电机
- 导入ONNX模型 *(可选)*
- 操作电机和传感器(或者调用ONNX模型)

# 构建示例项目(旋转指定电机并获取传感器值)
见 [test1](/code/pykos_examples/test1.py)

# 使用better_utils构建pyKOS机器人项目(可以直接下载[test.py](/code/test.py))
## 下载库文件
在本仓库下载[better_utils.py](/code/better_utils.py)并放入项目运行目录中
## 导入库文件
```python
import asyncio
from better_utils import BetterKOS
```
## 使用BetterKOS类
```python
async def main():
    async with BetterKOS('192.168.42.1', 50051) as kos:
        try:
            await kos.load_session('model_100.onnx')
            input('press to continue')
            await kos.loop()
        except:
            pass
        await kos.reset()
```
## 运行主函数
```python
asyncio.run(main())
```