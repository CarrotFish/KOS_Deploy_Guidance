# 简介
本文将通过官方示例介绍一些pyKOS的基本用法

[官方文档](https://kscalelabs.github.io/api-docs/pykos/actuator.html)

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
