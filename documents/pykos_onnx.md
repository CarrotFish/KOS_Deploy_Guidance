# 本项目内容：ONNX模型集成和pyKOS API调用

实现基于 [zeroth](https://github.com/kscalelabs) 的主控系统的一部分，主要用于：
- 集成并加载 ONNX 模型进行推理（控制策略、决策算法等）
- 利用 [pyKOS  API](https://kscalelabs.github.io/api-docs/pykos/actuator.html)实现对机器人动作的封装与指令控制

## 目录
- [本项目内容：ONNX模型集成和pyKOS API调用](#本项目内容onnx模型集成和pykos-api调用)
  - [目录](#目录)
  - [目标](#目标)
  - [项目架构](#项目架构)
  - [环境搭建](#环境搭建)
    - [1. ONNX 环境](#1-onnx-环境)
    - [2. pyKOS下载与安装](#2-pykos下载与安装)
    - [3. Genesis 仿真环境](#3-genesis-仿真环境)
  - [使用方法](#使用方法)
  - [后续工作](#后续工作)
## 目标

这周的工作旨在为第三组提供一个开箱即用的基础框架，使他们能专注于机器人控制算法的优化与调试，具体包括：
- **ONNX 模型集成：** 介绍如何将训练好的模型转换为 ONNX 格式，并在系统中加载和运行，实现对机器人的实时决策支持。
- **pyKOS API 封装：** 封装 pyKOS 的各项控制接口，对机器人动作进行简单封装，便于调用。

## 项目架构

项目主要由以下模块组成：
- `main.py`：程序入口，负责命令行参数解析、配置文件加载、日志系统初始化以及整体流程控制（未实现）
- `kos_api.py`：封装 pyKOS actuator 的调用方法，提供统一的机器人控制接口（未实现）
- `ONNX.md`：详细的 ONNX 模型转换和使用说明文档，帮助大家了解如何从训练模型到实际应用的全流程
- `config.yaml`：配置文件，记录机器人通信参数、控制参数等信息

## 环境搭建

为确保项目能正常运行，请按照以下步骤配置环境：

### 1. ONNX 环境

- **安装 onnxruntime：**  
  ONNX 模型将采用 [onnxruntime](https://github.com/microsoft/onnxruntime) 进行加载与推理：
  ```bash
  pip install onnxruntime
  ```
- **ONNX 模型转换工具：**  
  如果需要将 Pytorch/TensorFlow 模型转换为 ONNX 格式，请参考相应的官方文档，并在转换完成后利用 onnxruntime 加载模型。

### 2. pyKOS下载与安装

- **项目主页与文档：**  
  详细的 pyKOS API 使用说明参见 [pyKOS actuator API 文档](https://kscalelabs.github.io/api-docs/pykos/actuator.html)。
- **安装 pyKOS：**  
  目前 pyKOS API 可通过 pip 或从 GitHub 仓库克隆代码后安装：
  ```bash
  pip install pykos
  ```
  或者：
  ```bash
  git clone https://github.com/kscalelabs/pykos.git
  cd pykos
  python setup.py install
  ```

### 3. Genesis 仿真环境

- **Genesis 仿真平台：**  
  本项目在 Genesis 环境下进行仿真训练。请确保你已正确安装并配置 Genesis 环境。有关 Genesis 安装与配置详情，请参照团队内部文档或 Genesis 官方指南。

## 使用方法

1. **配置环境：**
   - 搭建 Python 虚拟环境，并安装上述依赖：
     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux/MacOS
     venv\Scripts\activate  # Windows
     pip install onnxruntime pyyaml pykos
     ```
2. **准备配置文件：**  
   在项目根目录下创建 `config.yaml` 文件，内容示例：
   ```yaml
   actuator:
     host: "127.0.0.1"
     port: 8000
   robot:
     speed: 5.0
   ```
3. **启动主控程序：**  
   通过命令行运行：
   ```bash
   python main.py --config config.yaml
   ```
   
4. **ONNX 模型部署：**  
   请参阅 `docs/ONNX.md` 获取详细教程：如何将训练好的模型转换为 ONNX 模型，并集成到主控系统中。


## 后续工作

- 持续完善 ONNX 模型在各场景下的应用示例。
- 对接更多 pyKOS API 功能，丰富机器人动作控制。
- 根据第三组的反馈，迭代优化与 Genesis 仿真环境的联调流程。