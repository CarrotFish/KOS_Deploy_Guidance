# 注意！本代码仍在测试阶段！

'''
本代码包括：
1.读取摄像头
2.提供测试,录制一段视频
'''

# kos\kos_sim均未提供摄像头调用的库，故在此尝试使用通用的方法去检查设备
import subprocess

# 检查设备
def list_cameras():
    result = subprocess.run(
        ["v4l2-ctl", "--list-devices"],
        capture_output=True, text=True, check=True
    )
    print(result.stdout)

if __name__ == "__main__":
    list_cameras()

import subprocess

# # 拍照测试
# subprocess.run(
#     ["fswebcam", "-d", "/dev/video0", "-r", "640x480",
#      "--no-banner", "test.jpg"],
#     check=True
# )

# # 打印到显示屏
# from rgbmatrix import RGBMatrix, RGBMatrixOptions
# from PIL import Image
# import time

# options = RGBMatrixOptions()
# options.rows = 32
# options.cols = 32
# options.chain_length = 1
# matrix = RGBMatrix(options=options)

# img = Image.open("test.jpg").resize(
#     (options.cols, options.rows)
# )
# matrix.SetImage(img)
# time.sleep(5)

