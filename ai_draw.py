from PIL import Image
import requests
import io

# ===================== 打印固定配置 =====================
PRINT_WIDTH = 576
MAX_HEIGHT = 1000

# 强制黑白线条风格
FIXED_BLACK_WHITE_RULE = (
    "minimalist line art, black lines on white background, "
    "clean lines, no color, no gray, no shadow"
)

# ========================================================

# ===================== 火山方舟配置 =====================
ARK_API_KEY = ""

MODEL_ID = ""

ARK_API_URL = (
    "https://ark.cn-beijing.volces.com/api/v3/images/generations"
)

GENERATE_IMAGE_SIZE = "1024x1024"

# ========================================================


def clean_prompt(text):

    useless_words = [
        "申请",
        "请求",
        "帮我",
        "生成"
    ]

    for word in useless_words:
        text = text.replace(word, "")

    return text.strip()


# ===================== 核心生图函数 =====================

def generate_draw(on_image=None, prompt=None):

    # 1.获取提示词（优先使用传入的prompt）
    if prompt is not None:
        user_prompt = prompt
        print(f"📥 使用编辑后的文本：{user_prompt}")
    else:
        try:

            with open(
                "recognized_text.txt",
                "r",
                encoding="utf-8"
            ) as f:

                user_prompt = f.read().strip()

            print(f"📥 已读取：{user_prompt}")

        except:

            user_prompt = "风景"

            print("⚠️ 使用默认关键词：风景")

    # 2.拼接提示词

    user_prompt = clean_prompt(user_prompt)

    final_prompt = (
        f"{user_prompt}, "
        f"{FIXED_BLACK_WHITE_RULE}"
    )

    print(f"🎨 最终提示词：{final_prompt}")

    try:

        headers = {
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json"
        }

        saved_images = []

        print("\n🔹 开始生成3张图片...\n")

        # 连续生成3次
        for i in range(3):

            print(f"🎨 正在生成第{i+1}张图片...")

            payload = {
                "model": MODEL_ID,
                "prompt": final_prompt,
                "size": GENERATE_IMAGE_SIZE
            }

            response = requests.post(
                ARK_API_URL,
                headers=headers,
                json=payload
            )

            if response.status_code != 200:

                print(
                    f"❌ 第{i+1}张生成失败："
                )

                print(response.text)

                continue

            result = response.json()

            image_url = result["data"][0]["url"]

            print(
                f"✅ 图片{i+1}链接：{image_url}"
            )

            img_response = requests.get(
                image_url
            )

            image = Image.open(
                io.BytesIO(img_response.content)
            ).convert("RGB")

            # 适配打印机尺寸

            w, h = image.size

            new_h = int(
                h * PRINT_WIDTH / w
            )

            new_h = min(
                new_h,
                MAX_HEIGHT
            )

            image = image.resize(
                (
                    PRINT_WIDTH,
                    new_h
                ),
                Image.Resampling.LANCZOS
            )

            # 固定覆盖保存

            save_path = (
                f"generated_{i+1}.jpg"
            )

            image.save(save_path)

            saved_images.append(
                save_path
            )

            print(
                f"💾 保存：{save_path}"
            )

            if on_image:
                on_image(save_path, i)

        print("\n🎉 三张图片生成完成")

        return saved_images

    except Exception as e:

        print(
            f"❌ 生成失败：{str(e)}"
        )

        return []


# ===================== 独立测试 =====================

if __name__ == "__main__":

    images = generate_draw()

    print("\n返回结果：")

    print(images)
