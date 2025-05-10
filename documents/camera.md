# Zeroth摄像头检查指南
## 一、通过SSH连接机器人
见robot.md

## 二、查看设备信息

**参考https://milkv.io/zh/docs/duo/camera/gc2083**



执行测试程序推流：
```bash
camera-test.sh
```
正常情况下，终端最后会看到如下日志：
```
Bind VI with VPSS Grp(0), Chn(0)
Attach VBPool(0) to VPSS Grp(0) Chn(0)
Attach VBPool(1) to VPSS Grp(0) Chn(1)
Initialize VENC
venc codec: h264
venc frame size: 1280x720
Initialize RTSP
rtsp://127.0.1.1/h264
prio:0
anchor:-8,-8,8,8
anchor:-16,-16,16,16
bbox:bbox_8_Conv_dequant
landmark:kps_8_Conv_dequant
score:score_8_Sigmoid_dequant
anchor:-32,-32,32,32
anchor:-64,-64,64,64
bbox:bbox_16_Conv_dequant
landmark:kps_16_Conv_dequant
score:score_16_Sigmoid_dequant
anchor:-128,-128,128,128
anchor:-256,-256,256,256
bbox:bbox_32_Conv_dequant
landmark:kps_32_Conv_dequant
score:score_32_Sigmoid_dequant
Enter TDL thread
Enter encoder thread
0 R:1165 B:3087 CT:2688
1 R:1464 B:2327 CT:3937
2 R:1974 B:1613 CT:7225
Golden 1464 1024 2327
```
注意 rtsp: 开头的链接，把 IP 改成 Duo 的 IP 就是我们要在 VLC 中拉流的地址了。

在PC上打开VLC播放器，菜单“媒体”中选择“打开网络串流”，选择“网络”标签，在“请输入网络URL”中输入：
```bash
rtsp://192.168.42.1/h264
```
点”播放“，就可以看到摄像头推流的画面了


## 三、报错解决
在终端输入命令：
```bash
cat /var/log/cvi_camera.log
```
*如果报错如下：*
```
[SAMPLE_COMM_SNS_ParseIni]-1950: Parse /mnt/data/sensor_cfg.ini
[parse_source_devnum]-1605: devNum =  1
[parse_sensor_name]-1686: sensor =  GCORE_GC2083_MIPI_2M_30FPS_10BIT
[parse_sensor_busid]-1714: bus_id =  3
[parse_sensor_i2caddr]-1725: sns_i2c_addr =  37
[parse_sensor_mipidev]-1736: mipi_dev =  0
[parse_sensor_laneid]-1747: Lane_id =  2, 0, 1, -1, -1
[parse_sensor_pnswap]-1758: pn_swap =  0, 0, 0,  0,  0
MMF Version:7e0cc6a08-musl_riscv64
Create VBPool[0], size: (3110400 * 2) = 6220800 bytes
Create VBPool[1], size: (1382400 * 2) = 2764800 bytes
Total memory of VB pool: 8985600 bytes
Initialize SYS and VB
Initialize VI
ISP Vipipe(0) Allocate pa(0x95b92000) va(0x0x3fdc862000) size(291120)
stSnsrMode.u16Width 1920 stSnsrMode.u16Height 1080 25.000000 wdrMode 0 pstSnsObj 0x3fdd689878
[SAMPLE_COMM_VI_StartMIPI]-483: sensor 0 stDevAttr.devno 0
vi init failed. s32Ret: 0xffffffff !
init middleware failed! ret=ffffffff
```

还可以检查内核配置`cat /proc/config.gz | gunzip` 

具体如何解决：
//TODO