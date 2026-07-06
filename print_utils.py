# print_utils.py - 修复版：懒加载串口，调试输出完整，100%复用原有打印逻辑
import time
import os
from PIL import Image
from gui_constants import PRINT_WIDTH, COM_PORT, BAUD_RATE, PROCESSED_PHOTO_PATH

# ========== 打印参数（完全沿用你原有配置） ==========
CHUNK_SIZE = 1024
HEAT_DOTS  = 9
HEAT_TIME  = 80
HEAT_GAP   = 2
ENABLE_DENSITY = False
TX_DELAY   = 0.01

ser = None
_MOCK = None  # None=未初始化，True/False=已初始化

def _init_serial():
    """按需初始化串口，失败自动降级模拟模式"""
    global ser, _MOCK
    if _MOCK is not None:
        return  # 已经初始化过了
    
    print("  正在连接打印机...", flush=True)
    try:
        import serial
        ser = serial.Serial(
            port=COM_PORT, 
            baudrate=BAUD_RATE, 
            timeout=2, 
            write_timeout=2
        )
        _MOCK = False
        print(f"  ✅ 串口已连接：{COM_PORT}", flush=True)
    except Exception as e:
        _MOCK = True
        print(f"  ⚠️  串口 {COM_PORT} 不可用（{e}），降级为模拟模式", flush=True)

def send_data(data):
    if _MOCK:
        print(f"  [模拟] 发送 {len(data)} 字节", flush=True)
        return
    try:
        for i in range(0, len(data), CHUNK_SIZE):
            ser.write(data[i:i + CHUNK_SIZE])
            time.sleep(TX_DELAY)
    except Exception as e:
        print(f"  数据发送失败：{e}", flush=True)

def printer_init():
    """打印机初始化（完全复用你原有的指令）"""
    _init_serial()  # 确保串口已初始化
    if _MOCK:
        print("  [模拟] 打印机初始化", flush=True)
        return
    # ESC @ 初始化
    send_data(b'\x1B\x40')
    time.sleep(0.1)
    # 设置GBK代码页
    send_data(b'\x1B\x74\xFF')
    time.sleep(0.02)
    # 可选打印浓度
    if ENABLE_DENSITY:
        send_data(bytes([0x1B, 0x37, HEAT_DOTS, HEAT_TIME, HEAT_GAP]))
        time.sleep(0.05)

def image_to_bw(img):
    """二值化（和你原有逻辑完全一致）"""
    img = img.convert("L")
    img = img.point(lambda x: 0 if x < 80 else 255, '1')
    return img

def _print_image_by_path(image_path):
    """打印指定路径的图片"""
    try:
        if not os.path.exists(image_path):
            print(f"  ❌ 打印失败：图片不存在 → {image_path}", flush=True)
            return False
        
        print("  处理图片...", flush=True)
        img = Image.open(image_path)
        img = image_to_bw(img)
        img = img.resize((PRINT_WIDTH, int(img.height * PRINT_WIDTH / img.width)))
        width = PRINT_WIDTH
        height = img.height
        width_bytes = width // 8

        cmd = bytearray()
        cmd += b'\x1D\x76\x30\x00'  # GS v 0 光栅位图指令
        cmd += bytes([width_bytes % 256, width_bytes // 256])
        cmd += bytes([height % 256, height // 256])

        for y in range(height):
            for x in range(0, width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < width:
                        pixel = img.getpixel((x + bit, y))
                        if pixel == 0:
                            byte |= (1 << (7 - bit))
                cmd.append(byte)

        print("  发送图片数据...", flush=True)
        send_data(cmd)
        time.sleep(2)

        if _MOCK:
            img.save("print_preview.bmp")
            print("  [模拟] 预览已保存为 print_preview.bmp", flush=True)
        else:
            print("  ✅ 图片打印完成", flush=True)
        return True
    except Exception as e:
        print(f"  图片处理失败：{e}", flush=True)
        return False

def print_feed(lines=2):
    """进纸"""
    try:
        if not _MOCK:
            send_data(b'\x1B\x64' + bytes([min(lines, 255)]))
        else:
            print(f"  [模拟] 进纸 {lines} 行", flush=True)
    except Exception as e:
        print(f"  进纸失败：{e}", flush=True)

def close_printer():
    """关闭串口"""
    global ser, _MOCK
    try:
        if ser and ser.is_open:
            ser.close()
            print("  串口已关闭", flush=True)
    except Exception as e:
        print(f"  关闭串口失败：{e}", flush=True)
    finally:
        ser = None
        _MOCK = None

def print_photo(image_path=PROCESSED_PHOTO_PATH):
    """对外打印入口"""
    try:
        print("\n========== 开始打印 ==========\n", flush=True)
        printer_init()
        success = _print_image_by_path(image_path)
        if success:
            print_feed(30)
            print("\n✅ 打印全部完成！\n", flush=True)
        return success
    except Exception as e:
        print(f"\n❌ 打印流程失败：{e}", flush=True)
        return False
    finally:
        close_printer()

# 单独测试入口
if __name__ == "__main__":
    print("===== 打印测试开始 =====", flush=True)
    print(f"目标图片：{PROCESSED_PHOTO_PATH}", flush=True)
    result = print_photo(PROCESSED_PHOTO_PATH)
    print(f"===== 测试结束，结果：{'成功' if result else '失败'} =====", flush=True)