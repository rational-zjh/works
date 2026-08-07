import sys
import os
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QMovie, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包后的路径）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MultiGifPet(QWidget):
    def __init__(self, sleep_gif, eat_gif, target_width=120):
        super().__init__()

        self.sleep_gif_path = get_resource_path(sleep_gif)
        self.eat_gif_path = get_resource_path(eat_gif)
        self.target_width = target_width  # 设置桌宠固定宽度（像素）

        # 检查文件是否存在
        for path in [self.sleep_gif_path, self.eat_gif_path]:
            if not os.path.exists(path):
                print(f"错误: 找不到素材文件 '{path}'。")
                sys.exit(1)

        # 当前状态: 'sleep' 或 'eat'
        self.state = 'sleep'

        # 1. 初始化 UI
        self.initUI()

        # 2. 创建各自状态的 QMovie
        self.movies = {
            'sleep': QMovie(self.sleep_gif_path),
            'eat': QMovie(self.eat_gif_path)
        }

        # 预处理两个 GIF 的缩放比例
        self.setup_movie_sizes()

        # 3. 初始显示“睡觉”状态
        self.switch_state('sleep')

        self.drag_offset = QPoint()
        self.is_dragging = False

    def initUI(self):
        """设置窗口无边框、置顶与背景透明"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.setStyleSheet("background:transparent;")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.show()

    def setup_movie_sizes(self):
        """
        根据各自 GIF 的原始宽高比，算出各自在指定宽度下的合适高度，
        确保不同比例的 GIF 缩放后都不会拉伸变形。
        """
        for state, movie in self.movies.items():
            movie.start()
            orig_size = movie.frameRect().size()

            if orig_size.isValid() and orig_size.width() > 0:
                # 按照各自的宽高比单独计算高度
                new_height = int(orig_size.height() * (self.target_width / orig_size.width()))
                movie.setScaledSize(QSize(self.target_width, new_height))

            movie.stop()  # 预处理完毕后暂停

    def switch_state(self, new_state):
        """切换桌宠状态（睡觉 ↔ 吃饭）"""
        # 如果已经处于要切换的状态，直接返回
        if self.state == new_state and self.label.movie() == self.movies[new_state]:
            return

        # 停止当前正在播放的 GIF
        if self.state in self.movies:
            self.movies[self.state].stop()

        self.state = new_state
        current_movie = self.movies[self.state]

        # 绑定新的 QMovie 并开始循环播放
        self.label.setMovie(current_movie)
        current_movie.start()

        # 根据当前 GIF 缩放后的专属尺寸，动态调整 label 和主窗口的大小
        scaled_size = current_movie.scaledSize()
        self.label.resize(scaled_size)
        self.resize(scaled_size)

    # --- 鼠标点击与拖拽处理 ---

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.pos()
            self.is_dragging = False
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.is_dragging = True
            self.move(event.globalPos() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 仅在松开左键时结束拖拽状态，不再触发任何状态切换
            self.is_dragging = False
            event.accept()

    # --- 右键菜单（唯一的状态切换入口） ---

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        # 状态切换选项
        eat_action = QAction("🍖 吃饭", self)
        eat_action.triggered.connect(lambda: self.switch_state('eat'))
        menu.addAction(eat_action)

        sleep_action = QAction("💤 睡觉", self)
        sleep_action.triggered.connect(lambda: self.switch_state('sleep'))
        menu.addAction(sleep_action)

        menu.addSeparator()

        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    sleep_material = "cat_sleep_transparent.gif"
    eat_material = "cat_eat_res_transparent.gif"

    pet = MultiGifPet(
        sleep_gif=sleep_material,
        eat_gif=eat_material,
        target_width=200
    )

    sys.exit(app.exec_())