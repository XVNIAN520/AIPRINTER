# camera_utils.py - 修复版：解决进程卡死、无输出问题
import subprocess
import os
import signal
import time
import sys
from gui_constants import (
    CAMERA_DEVICE, DISPLAY_ENV,
    PREVIEW_WIDTH, PREVIEW_HEIGHT, PREVIEW_FPS,
    CAPTURE_WIDTH, CAPTURE_HEIGHT,
    RAW_PHOTO_PATH
)

preview_process = None

def _kill_all_gst():
    """轻量兜底：快速杀残留进程，不阻塞"""
    try:
        subprocess.Popen(["pkill", "-9", "gst-launch-1.0"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
    except:
        pass

def check_camera_device():
    return os.path.exists(CAMERA_DEVICE)

def start_camera_preview(window_id=None):
    """启动摄像头预览（修复版：无管道阻塞）
    window_id: X11 窗口 ID（十进制整数），传入则嵌入该窗口；None 则用独立窗口。
    """
    global preview_process
    
    # 先停掉旧的
    stop_camera_preview()
    
    if not check_camera_device():
        print(f"错误：摄像头设备 {CAMERA_DEVICE} 不存在", flush=True)
        return False

    # 根据是否传入 window_id 选择 sink
    if window_id is not None:
        # xvimagesink：XVideo 硬件加速；如果板子不支持可换 ximagesink
        sink = f"ximagesink window-handle={window_id}"
    else:
        sink = "autovideosink"

    cmd = [
        "gst-launch-1.0",
        "v4l2src", f"device={CAMERA_DEVICE}",
        "!", f"image/jpeg,width={PREVIEW_WIDTH},height={PREVIEW_HEIGHT},framerate={PREVIEW_FPS}",
        "!", "jpegdec",
        "!", "videoconvert",
        "!", *sink.split()
    ]

    # 注入显示环境
    env = os.environ.copy()
    env["DISPLAY"] = DISPLAY_ENV

    try:
        # 关键修复：输出全部丢DEVNULL，不接PIPE，永远不会缓冲区满
        preview_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env
        )
        time.sleep(1)  # 等1秒让窗口弹出来
        
        if preview_process.poll() is None:
            print("✅ 摄像头预览启动成功", flush=True)
            return True
        else:
            print("❌ 预览启动失败，进程立刻退出了", flush=True)
            if window_id is not None:
                print("   提示：xvimagesink 可能不可用，可尝试换 ximagesink", flush=True)
            return False
    except Exception as e:
        print(f"❌ 预览启动异常：{e}", flush=True)
        return False

def stop_camera_preview():
    """停止预览"""
    global preview_process
    
    if preview_process is None:
        return True
    
    if preview_process.poll() is not None:
        preview_process = None
        return True

    try:
        # 先软杀
        preview_process.terminate()
        try:
            preview_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            # 超时强杀
            preview_process.kill()
            preview_process.wait(timeout=2)
        preview_process = None
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"停止预览异常：{e}", flush=True)
        _kill_all_gst()
        preview_process = None
        return False

def capture_photo():
    """拍照（完全复用你验证过的指令）
    返回：(是否成功, 错误信息)
    """
    # 先停预览
    stop_camera_preview()
    time.sleep(0.5)

    if not check_camera_device():
        return False, f"摄像头设备 {CAMERA_DEVICE} 不存在"

    # 100% 照搬你给的标准拍照指令
    cmd = [
        "gst-launch-1.0",
        "v4l2src", f"device={CAMERA_DEVICE}",
        "num-buffers=5",
        "!", "queue",
        "!", "videoconvert",
        "!", "jpegenc",
        "!", "filesink", f"location={RAW_PHOTO_PATH}"
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=10
        )
        
        if result.returncode == 0 and os.path.exists(RAW_PHOTO_PATH):
            print(f"✅ 拍照成功，保存至：{RAW_PHOTO_PATH}", flush=True)
            return True, ""
        else:
            err = result.stderr.decode("utf-8", errors="ignore")
            print(f"❌ 拍照失败：{err[:200]}", flush=True)
            return False, f"拍照失败：{err[:200]}"
    except subprocess.TimeoutExpired:
        _kill_all_gst()
        return False, "拍照超时，已释放摄像头"
    except Exception as e:
        _kill_all_gst()
        return False, f"拍照异常：{str(e)}"

def capture_preview_frame(output_path="/tmp/cam_preview_frame.jpg"):
    """抓取一帧预览画面（JPEG），保存到 output_path。
    返回 True/False。不依赖任何特殊 sink，纯命令行。
    """
    if not check_camera_device():
        return False

    cmd = [
        "gst-launch-1.0",
        "v4l2src", f"device={CAMERA_DEVICE}", "num-buffers=1",
        "!", f"image/jpeg,width={PREVIEW_WIDTH},height={PREVIEW_HEIGHT}",
        "!", "filesink", f"location={output_path}"
    ]

    env = os.environ.copy()
    env["DISPLAY"] = DISPLAY_ENV

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            timeout=3
        )
        return result.returncode == 0 and os.path.exists(output_path)
    except Exception:
        return False


# 测试入口
if __name__ == "__main__":
    print("===== 摄像头测试开始 =====", flush=True)
    print("启动预览中...", flush=True)
    
    ok = start_camera_preview()
    if not ok:
        print("预览启动失败，退出测试", flush=True)
        sys.exit(1)
    
    input("\n预览窗口已弹出，调整好角度后按回车键拍照...")
    
    ok, msg = capture_photo()
    if ok:
        print("\n测试全部成功！去桌面看 cap.jpg 即可", flush=True)
    else:
        print(f"\n测试失败：{msg}", flush=True)
    
    print("===== 测试结束 =====", flush=True)