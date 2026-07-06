# image_processing.py - AI线稿生成版（修复base64传图格式）
import requests
import base64
import io
import os
from PIL import Image
from gui_constants import RAW_PHOTO_PATH, PROCESSED_PHOTO_PATH

# ========== 复用你原有AI绘图的API配置 ==========
ARK_API_KEY = ""
MODEL_ID = "ep-20260414192828-b5wrm"
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

# ========== 线稿提示词 ==========
LINE_ART_PROMPT = """请参考上传的图片，将图片主体转换成适合打印上色的简洁卡通线稿图。
要求：
1. 保留原图主体的基本轮廓、姿态和主要识别特征；
2. 整体转换为简洁可爱的卡通风格，适度概括造型，不要失真；
3. 黑白线稿，纯白背景，只保留主体，不要背景；
4. 使用清晰、流畅、连续的黑色轮廓线；
5. 尽量减少内部复杂细节，减少碎小线条，只保留关键结构；
6. 外轮廓明确，内部结构尽量简洁，形成清楚、较大的封闭上色区域；
7. 去除复杂背景、阴影、灰度、渐变、照片纹理和杂乱元素；
8. 不要彩色，不要灰色阴影，不要素描排线，不要写实效果，不要过于复杂的细节。
输出：一张干净、简洁、适合打印和上色的卡通线稿图。
"""


def convert_to_line_art(
    input_path=RAW_PHOTO_PATH,
    output_path=PROCESSED_PHOTO_PATH,
    prompt=LINE_ART_PROMPT
):
    """
    调用火山方舟图生图API，将实拍照片转为AI卡通线稿
    返回：(是否成功, PIL图像对象/None, 错误信息)
    """
    if not os.path.exists(input_path):
        err = f"输入图片不存在：{input_path}"
        print(err, flush=True)
        return False, None, err

    try:
        # 1. 读取本地图片并转base64
        with open(input_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")

        # 2. 构造请求头和参数（修复：base64包装成标准data URL格式）
        headers = {
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_ID,
            "prompt": prompt,
            "image": f"data:image/jpeg;base64,{img_base64}",  # 关键修复：加上data URI前缀
            "size": "1024x1024",
            "response_format": "url"
        }

        print("🎨 AI正在生成线稿...", flush=True)
        response = requests.post(ARK_API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            err = f"API调用失败：{response.status_code} - {response.text[:300]}"
            print(err, flush=True)
            return False, None, err

        result = response.json()
        image_url = result["data"][0]["url"]

        # 3. 下载生成的线稿
        img_resp = requests.get(image_url, timeout=20)
        out_img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")

        # 4. 适配打印尺寸
        from gui_constants import PRINT_WIDTH
        w, h = out_img.size
        new_h = int(h * PRINT_WIDTH / w)
        out_img = out_img.resize((PRINT_WIDTH, new_h), Image.Resampling.LANCZOS)

        # 5. 保存到固定路径（覆盖，确保打印最新图）
        out_img.save(output_path)
        print(f"✅ AI线稿生成成功，保存至：{output_path}", flush=True)
        return True, out_img, ""

    except Exception as e:
        err = f"生成失败：{str(e)}"
        print(err, flush=True)
        return False, None, err


# 单独测试入口
if __name__ == "__main__":
    print("===== AI线稿生成测试 =====", flush=True)
    ok, img, msg = convert_to_line_art()
    if ok:
        print("生成完成，可打开 processed_cap.jpg 查看效果", flush=True)
    else:
        print(f"失败：{msg}", flush=True)
