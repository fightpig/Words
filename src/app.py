from tkinter import ttk

from book import Book
from configuration import Config
from configuration import Params
from media import Audio
from main_ui import (
    RootWrapper,
    TitleWrapper,
    MainFrameWrapper,
    MenuFrameWrapper,
    ContentFrameWrapper,
)
from utils import RecorderHelper


class App:
    def __init__(
        self,
        app_name="Will Be Better Next Time",
        width=1280,
        height=768,
        save_mp4_dir_path="word-mp4",
    ):
        config = Config()
        book = Book(config=config)
        audio = Audio()
        params = Params()
        recorder_helper = RecorderHelper(save_mp4_dir_path)

        self.root = RootWrapper(
            title=app_name,
            width=width,
            height=height,
            book=book,
            audio=audio,
            params=params,
            recorder_helper=recorder_helper,
        )

    def layout(self):
        TitleWrapper(self.root)
        # 添加标题栏和内容区域的分隔线
        ttk.Separator(self.root.widget, orient="horizontal").pack(fill="x")
        main_frame = MainFrameWrapper(self.root)
        # 添加左菜单栏
        MenuFrameWrapper(main_frame)
        # 添加右内容区域
        ContentFrameWrapper(main_frame)

    def bind(self):
        pass

    @staticmethod
    def run(width=1280, height=768):
        app = App(width=width, height=height)
        app.layout()
        app.bind()
        app.root.widget.mainloop()


def main():
    App.run()


if __name__ == "__main__":
    main()
