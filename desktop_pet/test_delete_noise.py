import numpy as np
import cv2
from PIL import Image, ImageSequence
from rembg import remove


def clean_gif_noise(input_path, output_path):
    print("开始高清去噪处理，请稍等...")
    img = Image.open(input_path)

    frames = []
    durations = []

    for frame in ImageSequence.Iterator(img):
        durations.append(frame.info.get("duration", 100))

        # 1. AI 去背景
        transparent = remove(frame.convert("RGBA"))

        # 2. 转为 OpenCV 格式处理 Alpha 通道，去除孤立黑点
        np_img = np.array(transparent)
        alpha = np_img[:, :, 3]

        # 如果 Alpha 值太低（边缘半透明噪点），直接强制清零（变纯透明）
        alpha[alpha < 100] = 0

        # 形态学开运算：消除孤立小噪点
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)

        np_img[:, :, 3] = alpha
        clean_frame = Image.fromarray(np_img)
        frames.append(clean_frame)

    # 3. 保存为干净的透明 GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )
    print(f"处理完成！干净的素材已保存至: {output_path}")


if __name__ == "__main__":
    # 需要先 pip install opencv-python numpy
    clean_gif_noise("cat_eat_res.gif", "cat_eat_res_transparent.gif")