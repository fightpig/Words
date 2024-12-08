import tkinter as tk
from tkinter import ttk

from article_ui import ArticleOperationFrameWrapper
from base import BaseWrapper, check_name
from utils import Binder, toggle_btn_color
from word_ui import WordOperationFrameWrapper, WordContentFrameWrapper


@check_name
class RootWrapper(BaseWrapper):
    name = "root_wrapper"

    def __init__(self, title: str, width=1280, height=768, **kwargs):
        self.title = title
        self.height = height
        self.width = width
        super().__init__(parent=None, **kwargs)

    def create(self):
        self.widget = tk.Tk()
        self.widget.geometry(f"{self.width}x{self.height}")
        self.widget.title(self.title)


@check_name
class TitleWrapper(BaseWrapper):
    """上标题栏"""

    name = "title_frame_wrapper"

    def __init__(self, parent: BaseWrapper):
        self.height = 100
        self.title = "NextBetter"
        self.font_size = 20
        self.font = "Arial"

        super().__init__(parent)

    def create(self):
        self.widget = ttk.Frame(self.parent.widget, height=self.height, name=self.name)
        self.widget.pack(side="top", fill="x")

        name = "title_label"
        title_label = ttk.Label(
            self.widget, text=self.title, font=(self.font, self.font_size), name=name
        )
        title_label.pack(side="left", padx=20, pady=20)
        self.sub_widgets["title_label"] = title_label


@check_name
class MainFrameWrapper(BaseWrapper):
    """下主区域"""

    name = "main_frame_wrapper"

    def __init__(self, parent: BaseWrapper):
        super().__init__(parent)

    def create(self):
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side="top", fill="both", expand=True)


@check_name
class MenuFrameWrapper(BaseWrapper):
    """菜单栏"""

    name = "menu_frame_wrapper"

    def __init__(self, parent: BaseWrapper):
        self.word_btn: tk.Button | None = None
        self.sentence_btn: tk.Button | None = None
        self.article_btn: tk.Button | None = None
        self.cur_page: str = "word"
        super().__init__(parent)

    def create(self):
        # 菜单栏
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side="left", fill="y")

        # 分隔线
        ttk.Separator(self.widget, orient="vertical").pack(
            side="right", fill="y", padx=2
        )

        name = f"{self.name}-word_btn"
        self.word_btn = ttk.Button(self.widget, text="单词", name=name)
        self.word_btn.pack(side="top", pady=10)
        self.sub_widgets[name] = self.word_btn

        name = f"{self.name}-sentence_btn"
        self.sentence_btn = ttk.Button(self.widget, text="句子", name=name)
        self.sentence_btn.pack(side="top", pady=10)
        self.sub_widgets[name] = self.sentence_btn

        name = f"{self.name}-article_btn"
        self.article_btn = ttk.Button(self.widget, text="文章", name=name)
        self.article_btn.pack(side="top", pady=10)
        self.sub_widgets[name] = self.article_btn

    def bind(self):
        Binder.click(self.word_btn, self.on_click_word_btn)
        Binder.click(self.sentence_btn, self.on_click_sentence_btn)
        Binder.click(self.article_btn, self.on_click_article_btn)

    def on_click_word_btn(self, event: tk.Event | None = None):
        toggle_btn_color([self.word_btn, self.sentence_btn, self.article_btn])
        if self.cur_page != "word":
            content_frame_wrapper = self.get_wrapper("content_frame_wrapper")
            content_frame_wrapper.destroy_widget()
            self.cur_page = "word"
            content_frame_wrapper.create(page=self.cur_page)

    def on_click_sentence_btn(self, event: tk.Event | None = None):
        # TODO
        pass

    def on_click_article_btn(self, event: tk.Event | None = None):
        toggle_btn_color([self.article_btn, self.word_btn, self.sentence_btn])
        if self.cur_page != "article":
            content_frame_wrapper = self.get_wrapper("content_frame_wrapper")
            content_frame_wrapper.destroy_widget()
            self.cur_page = "article"
            content_frame_wrapper.create(page=self.cur_page)


@check_name
class ContentFrameWrapper(BaseWrapper):
    """右侧内容区域"""

    name = "content_frame_wrapper"

    def __init__(self, parent: BaseWrapper):
        self.cur_page: str = "word"
        super().__init__(parent)

    def create(self, page="word"):
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side="top", fill="both", expand=True)

        match page:
            case "word":
                # 添加操作栏
                WordOperationFrameWrapper(self)
                # 添加水平分隔线
                ttk.Separator(self.widget, orient="horizontal").pack(fill="x")
                # 添加单词显示区域
                WordContentFrameWrapper(self)
            case "sentence":
                pass
            case "article":
                ArticleOperationFrameWrapper(self)
                # 添加水平分隔线
                ttk.Separator(self.widget, orient="horizontal").pack(fill="x")
                # 添加单词显示区域
                # ArticleContentFrameWrapper(self)
            case _:
                pass
