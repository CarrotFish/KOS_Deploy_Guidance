# 机器人端系统烧录
## 下载系统镜像文件
前往[官方仓库](https://gitlab.kscale.ai/zeroth-robotics/OpenLCH-buildroot/-/artifacts)下载最新版artifacts.zip，解压直到出现一个.zip文件(如果网站打不开，请在群里戳我们，我们会把文件传到群里)

## 通过balenaEtcher烧录到SD卡
- 安装[Etcher](https://etcher.balena.io)
- 使用读卡器/SD卡插槽将SD卡连接电脑
- 打开Etcher，根据提示使用Etcher烧录

# 机器人电机配置
## 电机编号烧录须知
经过我们的真机测试，发现电机初始化ID为1，所以我们需要在 **运行应用之前** 将对应电机的ID烧录进电机的控制芯片。以下是电机编号对应表：

| ID   | 英文代号     | 对应位置     |
|------|-------------|-------------|
| 11 | left_shoulder_yaw |  |
| 12 | left_shouder_pitch |  |
| 13 | left_elbow |  |
| 21 | right_shoulder_yaw |  |
| 22 | right_shoulder_pitch |  |
| 23 | right_elbow |  |
| 31 | left_hip_yaw |  |
| 32 | left_hip_roll |  |
| 33 | left_hip_pitch |  |
| 34 | left_knee |  |
| 35 | left_ankle |  |
| 41 | right_hip_yaw |  |
| 42 | right_hip_roll |  |
| 43 | right_hip_pitch |  |
| 44 | right_knee |  |
| 45 | right_ankle |  |

## 烧录步骤
- 使用ssh命令连接开发办(以有线连接为例，初始密码为 milkv )
```bash
ssh root@192.168.42.1
```
- 按照电机安装顺序，每次安装一个，分别执行以下命令：
```bash
feetech_change_id 1 [对应ID]
```
- 查询电机情况
```bash
feetech_scan
feetech_identify [测试电机ID]
```