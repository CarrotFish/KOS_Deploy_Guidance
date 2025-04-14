# 环境配置(Windows)
## 安装Visual Studio编译工具
- 到[Visual Studio官网](https://visualstudio.com/)下载Visual Studio Installer
- 打开Installer，安装“MSVC 生成工具(最新)”、“Windows SDK”、“CMAKE windows平台”、“Git工具”
## 安装Anaconda
到[Anaconda官网](https://anaconda.org/)下载安装Anaconda
## 配置Conda虚拟环境
- 打开 Anaconda Prompt
- 创建本地环境
  
  ```bash
  conda create -p 你的环境目录 python=3.12.9
  ```
  
- 激活Conda环境

  ```bash
  conda activate 你的环境目录
  ```

## 安装pyKOS
- 使用pip安装pykos
  ```bash
  pip install pykos kos-sim
  ```
- 安装指定版本的protobuf
  ```bash
  pip install protobuf==5.29.0
  ```
- 进入Python环境查看是否安装完成
  ```bash
  python
  >>> import pykos
  ```
- 尝试运行kos-sim
  ```bash
  kos-sim kbot-v1
  ```
- 如果需要，可用从[官方仓库](https://github.com/kscalelabs/kos-sim)下载示例代码
