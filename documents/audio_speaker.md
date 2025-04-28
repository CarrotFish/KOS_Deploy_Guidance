# Zeroth机器人扬声器和麦克风检查指南
## 一、通过SSH连接机器人
见robot.md

## 二、查看设备信息
在成功连接到机器人的远程终端后，我们可以运行命令来查看机器人上的音频设备信息。
1. **查看录音设备**：运行命令`arecord -l`，正常情况下，会显示类似如下内容：
```
**** List of CAPTURE Hardware Devices ****
card 0: cv182xaadc [cv182xa_adc], device 0: cviteka-adc 300a100.adc-0 [cviteka-adc 300a100.adc-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```
这里，“card 0”表示声卡编号为0，“cv182xaadc”是声卡的名称，“[cv182xa_adc]”是更详细的声卡标识；“device 0”表示该声卡下的设备编号为0，“cviteka-adc 300a100.adc-0”是设备名称，“[cviteka-adc 300a100.adc-0]”是设备的详细标识；“Subdevices”表示子设备信息，这里显示该设备只有1个子设备，编号为0
2. **查看播放设备**：运行命令`aplay -l`，正常输出如下：
```
**** List of PLAYBACK Hardware Devices ****
card 1: cv182xadac [cv182xa_dac], device 0: cviteka-dac 300a000.dac-0 [cviteka-dac 300a000.dac-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```
其参数含义与录音设备类似，“card 1”表明这是编号为1的声卡，用于播放音频，“device 0”是该声卡下的播放设备

### 音频参数解释
1. **声道**：常见的声道类型有“mono”（单声道）和“stereo”（立体声）
2. **采样频率**：在音频处理中，采样频率是指每秒对声音信号进行采样的次数，单位是赫兹（Hz）

## 三、测试麦克风和扬声器
1. **录制音频**：运行命令`arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav`，其中：
    - `-D hw:0,0`：指定使用第一个声卡（card 0）的第一个设备（device 0）进行录音，也就是前面通过`arecord -l`查到的录音设备
    - `-f S16_LE`：设置音频文件格式为16位小端格式。在计算机存储数据时，“小端”模式是将数据的低位字节存储在内存的低地址端，这种格式在音频处理中较为常用
    - `-r 16000`：将采样率设置为16000Hz，即每秒对声音进行16000次采样
    - `-c 1`：设置声道数为1，也就是单声道录音
    - `-d 5`：设定录音时长为5秒
输入该命令后，终端会显示“recording”，表示正在录音。录音结束后，通过`ls`命令查看当前目录，应该能看到生成的“test.wav”文件
2. **播放音频**：运行命令`aplay -D hw:1,0 -f S16_LE -r 16000 -c 1 test.wav`，这里的参数含义与录音命令类似，`-D hw:1,0`指定使用编号为1的声卡（card 1）的第一个设备（device 0）进行播放，也就是播放设备；其他参数要与录音时设置一致，才能正确播放录制的音频。如果能正常听到声音，说明扬声器工作正常。

## 四、音量调节
1. **命令行调节**：运行命令`amixer scontrols`，会列出所有音量控制项，例如：
```
Simple mixer control 'ADC',0
```
找到你想要调节的音量控制项（如这里的“ADC”），然后运行`amixer sset 'ADC' 100%`，即可将该音量控制项设置为100%。你也可以根据需要设置其他百分比数值。
2. **图形界面调节**：运行命令`alsamixer -c 1`，会弹出一个图形界面。在这个界面中，通过上下箭头键可以调节音量大小，调节完成后按“Esc”键退出。


**其他：**
为了排除是麦克风问题还是扬声器问题，可以在本地终端（注意！不是ssh）运行命令
```bash
scp -O root@192.168.42.1:/root/test1.wav ~/Downloads/
```
请自己修改`~/Downloads/`部分！这行命令会通过scp传输，把test1.wav文件传到你的电脑，你可以进行检查

*参考：https://zhuanlan.zhihu.com/p/813448431*