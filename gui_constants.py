# gui_constants.py - 全局统一配置，所有模块共用
import os

# ========== 摄像头配置（对应你验证可用的参数） ==========
CAMERA_DEVICE = "/dev/video21"    # 摄像头设备号
DISPLAY_ENV = ":0.0"              # 预览窗口显示环境
# 预览分辨率/帧率
PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
PREVIEW_FPS = "30/1"
# 拍照分辨率
CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480

# ========== 图片路径配置 ==========
DESKTOP_PATH = "/home/elf/Desktop"
RAW_PHOTO_PATH = os.path.join(DESKTOP_PATH, "cap.jpg")          # 实拍原图路径
PROCESSED_PHOTO_PATH = os.path.join(DESKTOP_PATH, "processed_cap.jpg")  # AI线稿成品路径

# ========== 打印配置（对应你验证可用的参数） ==========
PRINT_WIDTH = 576                 # 热敏打印机打印宽度（像素）
PRINT_MAX_HEIGHT = 1000           # 最大打印高度，防止超长
COM_PORT = "/dev/ttyS9"           # 打印机串口
BAUD_RATE = 9600                  # 串口波特率