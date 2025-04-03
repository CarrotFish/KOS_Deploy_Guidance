# 简介
本项目是使用python的KOS编程的社区中文文档。

[K-Scale 官网](https://www.kscale.dev/)

# 环境配置(Windows)
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

- 安装Rust，准备编译KOS Python工具包

  ```bash
  conda install rust
  ```

- 使用Git下载KOS源码
  ```bash
  git clone https://github.com/kscalelabs/kos.git
  ```

- 编译KOS源码
  ```bash
  cd kos
  cargo build
  ```
- 进入Python环境查看是否安装完成
  ```bash
  python
  >>> import pykos
  ```
## 安装kos-sim(官方提供的一个简易的仿真环境)
- 使用pip安装kos-sim
  ```bash
  pip install kos-sim
  ```
- 尝试运行kos-sim
  ```bash
  kos-sim kbot-v1
  ```
- 如果需要，可用从[官方仓库](https://github.com/kscalelabs/kos-sim)下载示例代码
