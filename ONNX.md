# ONNX 模型转换与集成指南

介绍如何将使用 PyTorch 训练的模型转换为 ONNX 格式，并结合 pyKOS API 进行机器人控制。内容包括环境准备、转换步骤、模型验证以及如何将 ONNX 模型嵌入至主控系统中，最终实现与 Genesis 仿真环境的联调。

---

## 1. 介绍

ONNX（Open Neural Network Exchange）是一个开放的深度学习模型格式标准，可以实现在不同的深度学习框架之间进行模型互换。将 PyTorch 模型转换为 ONNX 模型，可以利用 [onnxruntime](https://github.com/microsoft/onnxruntime) 进行高效的推理，同时方便后续接入 pyKOS API，将推理结果转换为机器人控制指令。

---

## 2. 环境要求

在开始转换之前，请确保环境中已安装以下依赖：
- **PyTorch**
- **onnx** 与 **onnxruntime**：用于模型格式验证和推理。
- **pyKOS**：用于机器人控制接口的调用。

可使用如下命令安装依赖：

```bash
pip install torch onnx onnxruntime pykos
```

---

## 3. PyTorch 模型转换为 ONNX 模型

以下步骤介绍如何将 PyTorch 模型导出为 ONNX 格式：

### 3.1 模型准备

确保你的模型处于**评估模式**，这有助于冻结 BatchNorm 层和 Dropout 层的状态。例如：

```python
import torch
import torch.nn as nn

class Model(nn.Module):
    pass

model = Model()
model.eval()
```

### 3.2 导出 ONNX 模型

使用 `torch.onnx.export` 方法导出模型，定义一个与模型输入相同形状的 dummy tensor，并设置对应的导出参数：

```python
import torch

# 定义一个 dummy input，与实际输入形状保持一致
dummy_input = torch.randn(1, 10)

# 导出 ONNX 模型，输出文件命名为 model.onnx
torch.onnx.export(
    model,                           # 被转换的模型
    dummy_input,                     # 模拟输入张量
    "model.onnx",                    # 输出文件路径
    verbose=True,                    # 输出转换日志（可选）
    input_names=["input"],           # 输入名称（便于调试）
    output_names=["output"],         # 输出名称
    opset_version=11                 # ONNX 版本
)
```

转换完成后，会在当前目录生成 `model.onnx` 文件。

### 3.3 模型验证

为确保转换成功，可以使用 onnx 提供的检查工具验证导出的模型文件：

```python
import onnx

onnx_model = onnx.load("model.onnx")

onnx.checker.check_model(onnx_model)
print("check passed!")
```

---

## 4. ONNX 模型加载与推理

转换后的 ONNX 模型可以使用 onnxruntime 加载，并进行推理。下面是一个简单的推理示例：

```python
import onnxruntime as ort
import numpy as np

# 加载模型，创建 InferenceSession
session = ort.InferenceSession("model.onnx")

# 准备输入数据（注意数据类型和维度需与模型输入匹配）
input_data = np.random.randn(1, 10).astype(np.float32)

# 进行推理，返回结果
outputs = session.run(None, {"input": input_data})
print("output: ", outputs)
```

---

## 5. 接入 pyKOS API

在主控系统中，可将 ONNX 模型推理的结果用于生成机器人控制指令，通过 pyKOS API 下发指令。基本思路如下：

1. **加载 ONNX 模型并进行推理**：接收传感器数据后，调用 onnxruntime 推理接口，获得预测结果（例如预测动作或决策）。
2. **转换推理结果为控制指令**：根据模型输出，映射到机器人动作（如移动方向、速度调整等）。
3. **调用 pyKOS API 发送指令**：将转换后的指令通过 `actuator` 接口发送给仿真平台或机器人控制单元。

下面是一个集成示例，展示如何调用 ONNX 模型进行推理并利用 pyKOS API 发送一个简单的动作指令：

```python
import numpy as np
import onnxruntime as ort
from pykos import actuator  # 假设 pyKOS API 已正确安装

def load_model(model_path):
    session = ort.InferenceSession(model_path)
    return session

def run_inference(session, input_data):
    # 运行模型推理
    outputs = session.run(None, {"input": input_data})
    return outputs

def send_robot_command(result):
    # 简单示例：根据推理结果决定指令
    # 假设 result 为列表，若某个条件满足则发送 move 指令
    client = actuator.ActuatorClient(host="127.0.0.1", port=8000)
    if result[0].mean() > 0:
        response = client.move(speed=5.0, direction="forward")
    else:
        response = client.stop()
    print("pyKOS API 指令返回：", response)

if __name__ == "__main__":
    # 加载 ONNX 模型
    session = load_model("model.onnx")
    # 生成 dummy input
    input_data = np.random.randn(1, 10).astype(np.float32)
    # 运行推理
    outputs = run_inference(session, input_data)
    # 根据推理结果发送指令
    send_robot_command(outputs)
```

> **说明：**  
> 参考 [pyKOS actuator API 文档](https://kscalelabs.github.io/api-docs/pykos/actuator.html) 确保调用方法正确。

---

## 6. 常见问题与解决方案

- **转换过程中遇到运算不支持的问题：**  
  查看 [ONNX 官方文档](https://onnx.org.cn/onnx/intro/index.html) 中有关 op 和版本的说明，适时升级或修改模型代码以符合 ONNX 支持范围。
  
- **模型验证失败：**  
  检查导出参数设置是否正确，尤其是 input_names、output_names 和 opset_version。确保 dummy input 的 shape 与实际输入一致。

- **推理结果不如预期：**  
  可在 PyTorch 中先对模型进行调试，确保在 export 前模型输出正确，然后再进行转换和验证。

- **调用 pyKOS API 失败：**  
  请确保通信参数（如 host、port）配置正确，并检查 pyKOS API 文档中对应方法及参数要求。

---

## 7. 使用时请参考

- [ONNX 中文官网](https://onnx.org.cn/onnx/intro/index.html)
- [onnxruntime GitHub](https://github.com/microsoft/onnxruntime)
- [pyKOS actuator API 文档](https://kscalelabs.github.io/api-docs/pykos/actuator.html)

