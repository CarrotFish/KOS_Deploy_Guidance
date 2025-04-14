# 简介
本项目是使用python的KOS编程的社区中文文档。

[K-Scale 官网](https://www.kscale.dev/)

# KOS系统简介

K-Scale Operating System，是用于K-Scale机器人的操作系统，继承了对机器人底层硬件的处理、远程调用控制功能、仿真环境的系统。

我们控制机器人，分为下面几步：

- 在机器人侧的单片机上运行包含KOS软件包的Linux系统（烧录系统，接电会自动运行）。
- 让电脑和单片机连接到同一个网络，并在电脑上通过IP地址与端口号连接单片机。
- 在电脑上调用PyKOS提供的远程控制API，实现电机级控制与传感器原始数据读取。
- 通过强化学习，训练控制模型，实现高等功能。

为了搭建能够运行我们代码的软件环境，需要以下步骤

## 配置电脑端开发环境
见 [intallation.md](/documents/installation.md)

## 配置机器人端环境
见 [robot.md](/documents/robot.md)

## PyKOS API使用
见 [pyKOS.md](/documents/pyKOS.md)
