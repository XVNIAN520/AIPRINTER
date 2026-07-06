"""Linux 版：/dev/ttyUSB0 串口热敏打印机（厦门旻佑），串口不可用时自动降级为模拟模式
指令来源：
  - ESC指令集 完整版.pdf（厦门旻佑电子科技）
  - 厦门旻佑打印机指令集（精简版）.pdf
"""
import time
from PIL import Image

FINAL_PRINT_IMAGE = "final_print_image.jpg"
COM_PORT = "/dev/ttyS9"
BAUD_RATE = 9600
PRINT_WIDTH = 576
CHUNK_SIZE = 1024

# ── 可调参数（对应 ESC 7 打印浓度命令，完整版PDF 第46-47页） ──
# n1：最多加热点数，单位 8dots，默认 9（80 点），范围 0~255
#     最大加热点数 = 8 × (n1 + 1)
HEAT_DOTS  = 9     # 加热点数 n1，越大黑度/电流越大
HEAT_TIME  = 80    # 加热时间 n2，单位 10μs，默认 80（800μs），范围 0~255，越大越黑越慢
HEAT_GAP   = 2     # 加热间隔 n3，单位 10μs，默认 2（200μs），范围 0~255，越大越淡越快
ENABLE_DENSITY = False  # 是否发送打印浓度命令 ESC 7
TX_DELAY   = 0.01  # 每块数据发送间隔（秒）

# 尝试连接串口
ser = None
_MOCK = False
try:
    import serial
    ser = serial.Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=2, write_timeout=2)
    print(f"串口已连接：{COM_PORT}")
except Exception as e:
    _MOCK = True
    print(f"串口 {COM_PORT} 不可用（{e}），降级为模拟模式")

def send_data(data):
    if _MOCK:
        print(f"  [模拟] 发送 {len(data)} 字节")
        return
    try:
        for i in range(0, len(data), CHUNK_SIZE):
            ser.write(data[i:i + CHUNK_SIZE])
            time.sleep(TX_DELAY)
    except Exception as e:
        print(f"  数据发送失败：{e}")

def printer_init():
    """初始化打印机（完整版PDF 第46页 ESC @ = 1B 40）
       可选：设置打印浓度（完整版PDF 第46-47页 ESC 7 = 1B 37 n1 n2 n3）
       设置 GBK2312 代码页（完整版PDF 第14-15页 ESC t n = 1B 74 n，n=255 即 GBK2312）
    """
    if _MOCK:
        print("  [模拟] 打印机初始化")
        return
    # ESC @ — 初始化打印机，清除打印缓存、各参数恢复默认值
    send_data(b'\x1B\x40')
    time.sleep(0.1)
    # 设置字符代码页为 GBK2312（完整版PDF 第14-15页）
    send_data(b'\x1B\x74\xFF')
    time.sleep(0.02)
    # ESC 7 n1 n2 n3 — 设置打印浓度（完整版PDF 第46-47页）
    if ENABLE_DENSITY:
        send_data(bytes([0x1B, 0x37, HEAT_DOTS, HEAT_TIME, HEAT_GAP]))
        time.sleep(0.05)


def print_text(text):
    """文本打印（支持中文 GBK 编码）
       流程：进入汉字模式 → 设置 GBK 双字节编码 → 发送 GBK 文本 → 取消汉字模式
       精简版PDF 第1页示例：1B 40 1B 33 10 1D 21 11 1B 61 01 + GBK文本 + 0D 0A
       完整版PDF 第11页 FS & = 1C 26 进入汉字模式
       完整版PDF 第15-16页 ESC 9 n = 1B 39 n，n=0 为 GBK
    """
    try:
        if _MOCK:
            print(f"  [模拟] 打印标题: {text}")
            return
        # 进入汉字模式（完整版PDF 第11页 FS & = 1C 26）
        send_data(b'\x1C\x26')
        # 切换双字节编码为 GBK（完整版PDF 第15-16页 ESC 9 n，n=0）
        send_data(b'\x1B\x39\x00')
        # 居中对齐（完整版PDF 第10-11页 ESC a n，n=1 居中）
        send_data(b'\x1B\x61\x01')
        # 发送 GBK 编码文本
        send_data(text.encode('gbk'))
        # 换行（完整版PDF 第1页：0D 0A 为换行/结束符）
        send_data(b'\x0D\x0A')
        # 取消汉字模式（完整版PDF 第13页 FS . = 1C 2E）
        send_data(b'\x1C\x2E')
        print(f"  已打印文本：{text}")
    except Exception as e:
        print(f"  文本打印失败：{e}")


def image_to_bw(img):
    img = img.convert("L")
    img = img.point(lambda x: 0 if x < 80 else 255, '1')
    return img


def print_image():
    """光栅位图打印（完整版PDF 第17-18页 GS v 0 = 1D 76 30 m xL xH yL yH [d]k）
       m=0：正常模式（200×200 DPI），边传数据边打印，不需要再发打印指令
       精简版PDF 第3页示例：1D 76 30 00 07 00 2F 00 + 图片数据 + 0D 0A
       XX80 机型：水平字节数 1 ≤ xL+xH×256 ≤ 72，PRINT_WIDTH=576/8=72 恰好为上限
    """
    try:
        print("  处理图片...")
        img = Image.open(FINAL_PRINT_IMAGE)
        img = image_to_bw(img)
        img = img.resize((PRINT_WIDTH, int(img.height * PRINT_WIDTH / img.width)))
        width = PRINT_WIDTH
        height = img.height
        width_bytes = width // 8  # 72 bytes for 576px
        # 构建光栅位图命令头（完整版PDF 第17-18页）
        cmd = bytearray()
        cmd += b'\x1D\x76\x30\x00'  # GS v 0 m=0 正常模式
        cmd += bytes([width_bytes % 256, width_bytes // 256])  # xL, xH
        cmd += bytes([height % 256, height // 256])            # yL, yH
        # 图片数据：水平取模，每个字节 8 个水平像素，MSB 优先（bit7=最左像素）
        for y in range(height):
            for x in range(0, width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < width:
                        pixel = img.getpixel((x + bit, y))
                        if pixel == 0:
                            byte |= (1 << (7 - bit))
                cmd.append(byte)
        print("  发送图片数据...")
        send_data(cmd)
        time.sleep(2)  # 等待打印机完成打印
        if _MOCK:
            img.save("print_preview.bmp")
            print("  预览已保存为 print_preview.bmp")
        else:
            print("  图片打印完成")
    except Exception as e:
        print(f"  图片处理失败：{e}")


def print_feed(lines=2):
    """打印并进纸 n 行（完整版PDF 第2页 ESC d n = 1B 64 n）
       参数范围 0 ≤ n ≤ 255
    """
    try:
        if not _MOCK:
            send_data(b'\x1B\x64' + bytes([min(lines, 255)]))
        else:
            print(f"  [模拟] 进纸 {lines} 行")
    except Exception as e:
        print(f"  进纸失败：{e}")


def close_printer():
    try:
        if ser and ser.is_open:
            ser.close()
            print("  串口已关闭")
    except Exception as e:
        print(f"  关闭串口失败：{e}")


def print_final_image():
    try:
        print("\n========== 开始打印 ==========\n")
        # 初始化（含代码页设置）只做一次，后续 print_text 不再重复 init
        printer_init()

        # 标题
        print_text("AI Voice Printer")
        # 副标题
        print_text("RK3588 Demo")

        # 打印图片
        print_image()

        # 图片打印后走纸 12 行，留出撕纸空白
        print_feed(30)

        print("\n打印完成！\n")
        return True
    except Exception as e:
        print(f"\n打印流程失败：{e}")
        return False
    finally:
        close_printer()


if __name__ == "__main__":
    print_final_image()
