import pyaudio
import wave
import threading

# ===================== 固定配置 =====================
RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
FILENAME = "recording.wav"

# ⭐ 自动检测录音设备（RK3588 用 NAU8822，PC 用默认麦克风）
DEVICE_INDEX = None
# ====================================================

_stop_event = threading.Event()


def find_input_device(p):
    """自动找到可用输入设备"""
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info.get("name", "")
        # RK3588: 优先 NAU8822 / Rockchip
        if "nau8822" in name.lower() or "rockchip" in name.lower():
            if info.get("maxInputChannels", 0) > 0:
                print(f"  使用录音设备: {name} (index={i})")
                return i
    # PC: 使用系统默认设备
    try:
        default = p.get_default_input_device_info()
        print(f"  使用默认录音设备: {default.get('name', '未知')}")
    except:
        pass
    return None


def stop_recording():
    """外部调用，通知 record_audio 停止录音"""
    _stop_event.set()


def record_audio(duration=None):

    p = None
    stream = None

    try:
        p = pyaudio.PyAudio()

        global DEVICE_INDEX
        DEVICE_INDEX = find_input_device(p)

        print("🎤 开始录音...")
        _stop_event.clear()

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=DEVICE_INDEX,  # ⭐关键修复
            frames_per_buffer=CHUNK
        )

        frames = []

        if duration is None:
            # 持续录音，直到 stop_recording() 被调用
            while not _stop_event.is_set():
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception:
                    continue
        else:
            for _ in range(int(RATE / CHUNK * duration)):
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception:
                    continue

        print("🛑 录音结束")

        wf = wave.open(FILENAME, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        print(f"✅ 保存录音：{FILENAME}")

        return FILENAME

    except Exception as e:
        print("❌ 录音失败：", e)
        return None

    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()


if __name__ == "__main__":
    record_audio()