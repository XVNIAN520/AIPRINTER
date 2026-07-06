import wave
import json
from vosk import Model, KaldiRecognizer

# ===================== 模型路径 =====================
# Windows 示例: r"C:\vosk\vosk-model-cn-0.22"
# Linux 示例:   r"/home/elf/print/vosk-model-cn-kaldi-multicn-0.15"
ASR_MODEL_PATH = r"/home/elf/print/model"
# ====================================================

AUDIO_FILE = "recording.wav"
TEXT_FILE = "recognized_text.txt"


def audio_to_text():
    # 读取 WAV 音频文件
    try:
        print("📥 读取录音文件...")

        wf = wave.open(AUDIO_FILE, "rb")

        # 检查是否为单声道（ASR 要求单声道）
        if wf.getnchannels() != 1:
            print("⚠️ 不是单声道，请检查录音")
            return ""

        # 加载 ASR 模型并创建识别器
        model = Model(ASR_MODEL_PATH)
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        result_text = ""

        # 分段读取音频并识别
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text += res.get("text", "") + " "

        # 获取最终识别结果
        final_res = json.loads(rec.FinalResult())
        result_text += final_res.get("text", "")

        wf.close()

        # 空文本时给出默认提示
        result_text = result_text.strip() or "未识别到内容"

        # 保存识别结果到文件
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(result_text)

        print("✅ 识别完成")
        print("📝 文本：", result_text)

        return result_text

    except Exception as e:
        print("❌ 语音识别失败：", e)
        return ""