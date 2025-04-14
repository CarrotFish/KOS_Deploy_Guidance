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