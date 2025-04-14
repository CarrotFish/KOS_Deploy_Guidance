# KOS-SIM的相关问题
## 运行kos-sim
- 运行仿真环境
```bash
kos-sim kbot-v1
```
- 连接python程序
    将python程序中的机器人地址设成 localhost:50051
    在新的终端运行python程序
## 已知问题
- 运行python程序后，机器人上天
    - 尝试修改 kos.sim.reset()中pos.y的值，调在大概1.15左右，还不行可以调的更大一点
- 使用zbot-01的描述文件会在转换时报错，kbot的映射也是相同的也能用用，正在解决这个问题中