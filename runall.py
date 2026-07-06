from record import record_audio
from voice_to_text import audio_to_text
from ai_draw import generate_draw


def run_ai_pipeline():

    print("======= AI流程开始 =======")

    # 1.录音
    record_audio()

    # 2.语音转文字
    text = audio_to_text()

    # 3.生成三张图片
    images = generate_draw()

    print("======= AI流程结束 =======")

    return text, images


if __name__ == "__main__":

    text, images = run_ai_pipeline()

    print("\n识别结果：")
    print(text)

    print("\n生成图片：")
    print(images)