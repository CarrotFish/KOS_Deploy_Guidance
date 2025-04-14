#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pyKOS API 调用示例程序

本程序通过 pyKOS actuator API 实现与机器人控制模块的通信，
主要功能包括：
  - 解析命令行参数，加载配置文件（config.yaml）
  - 初始化 pyKOS actuator 客户端
  - 发送示例控制指令（如 move 指令）
  - 输出指令返回结果，便于调试和验证

请确保在运行前已安装如下依赖：
  pip install pyyaml pykos

配置文件示例（config.yaml）：
  actuator:
    host: "127.0.0.1"
    port: 8000
  robot:
    speed: 5.0
"""

import argparse
import logging
import yaml
from pykos import actuator  # 确保 pyKOS API 已正确安装

def init_logging():
    """初始化日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def parse_args():
    """解析命令行参数，支持指定配置文件"""
    parser = argparse.ArgumentParser(description="pyKOS API 调用程序")
    parser.add_argument(
        "--config", type=str, default="config.yaml", 
        help="配置文件路径，默认为 config.yaml"
    )
    return parser.parse_args()

def load_config(config_path):
    """加载 YAML 格式的配置文件"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.info("成功加载配置文件：%s", config_path)
        return config
    except Exception as e:
        logging.error("加载配置文件失败：%s", e)
        raise

def init_actuator_client(config):
    """根据配置文件参数初始化 pyKOS actuator 客户端"""
    try:
        client = actuator.ActuatorClient(
            host=config["actuator"]["host"],
            port=config["actuator"]["port"]
        )
        logging.info("成功初始化 pyKOS actuator 客户端")
        return client
    except Exception as e:
        logging.error("初始化 pyKOS actuator 客户端失败：%s", e)
        raise

def send_move_command(client, config):
    """
    发送示例 move 指令，根据配置文件中的机器人参数设置控制参数
    这里简单将机器人设定为“向前移动”，你可以根据需要扩展更多功能
    """
    try:
        speed = config["robot"].get("speed", 5.0)
        # 调用 pyKOS API 的 move 方法，具体方法及参数请参考官方文档
        response = client.move(speed=speed, direction="forward")
        logging.info("move 指令响应：%s", response)
    except Exception as e:
        logging.error("发送 move 指令时出错：%s", e)
        raise

def main():
    # 解析命令行参数
    args = parse_args()

    # 初始化日志输出
    init_logging()

    # 加载配置文件
    config = load_config(args.config)

    # 初始化 pyKOS actuator 客户端
    client = init_actuator_client(config)

    # 发送示例控制指令
    send_move_command(client, config)

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logging.critical("程序异常终止: %s", err)
