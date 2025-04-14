# 机器人端系统烧录
## 下载系统镜像文件
前往[官方仓库](https://gitlab.kscale.ai/zeroth-robotics/OpenLCH-buildroot/-/artifacts)下载最新版artifacts.zip，解压直到出现一个.zip文件(如果网站打不开，请在群里戳我们，我们会把文件传到群里)

## 通过balenaEtcher烧录到SD卡
- 安装[Etcher](https://etcher.balena.io)
- 使用读卡器/SD卡插槽将SD卡连接电脑
- 打开Etcher，根据提示使用Etcher烧录

# 机器人电机配置
## 电机编号烧录
经过我们的真机测试，发现电机初始化ID为1，所以我们需要在装配电机之前