import os
from PIL import Image, ImageSequence
from rembg import remove


def remove_gif_bg(input_path, output_path):
    print(f"开始处理 {input_path}，请稍等...")
    img = Image.open(input_path)

    frames = []
    durations = []

    # 逐帧读取 GIF
    for frame in ImageSequence.Iterator(img):
        # 记录每一帧的播放持续时间
        durations.append(frame.info.get("duration", 100))

        # 去除当前帧的背景
        transparent_frame = remove(frame.convert("RGBA"))
        frames.append(transparent_frame)

    # 将处理后的所有帧重新保存为透明 GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,  # 确保每一帧刷新时不留残影
    )
    print(f"成功！透明背景 GIF 已保存至: {output_path}")


if __name__ == "__main__":
    # 输入你原来的 GIF 路径，输出透明 GIF 路径
    remove_gif_bg("cat_eat.gif", "cat_eat_transparent.gif")