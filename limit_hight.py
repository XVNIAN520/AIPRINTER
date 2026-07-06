from PIL import Image

# ===================== 打印尺寸固定配置 =====================
PRINT_WIDTH = 576      # 80mm打印机标准宽度
MAX_HEIGHT = 1000     # 强制最大高度，防止无限出纸

# 最终打印文件（固定覆盖）
FINAL_PRINT_IMG = "final_print_image.jpg"
# ============================================================


# ===================== 图片限高处理函数 =====================
def limit_image_height(input_image):
    """
    对指定图片进行打印适配处理

    参数:
        input_image: 用户选择的图片路径

    输出:
        final_print_image.jpg
    """

    try:

        print(f"📥 读取图片：{input_image}")

        img = Image.open(input_image)

        w, h = img.size

        # 等比例缩放到打印机宽度
        scale = PRINT_WIDTH / w

        new_h = int(h * scale)

        # 限制最大高度
        if new_h > MAX_HEIGHT:
            new_h = MAX_HEIGHT

        resized_img = img.resize(
            (PRINT_WIDTH, new_h),
            Image.Resampling.LANCZOS
        )

        # 覆盖保存
        resized_img.save(FINAL_PRINT_IMG)

        print("✅ 图片尺寸处理完成")
        print(
            f"📏 最终尺寸：{PRINT_WIDTH} × {new_h}"
        )
        print(
            f"🖨️ 打印文件：{FINAL_PRINT_IMG}"
        )

        return FINAL_PRINT_IMG

    except Exception as e:

        print(f"❌ 图片处理失败：{e}")

        return None


# ===================== 独立测试 =====================
if __name__ == "__main__":

    limit_image_height(
        "generated_1.jpg"
    )