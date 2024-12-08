import tkinter as tk
from threading import Timer
from tkinter import ttk, messagebox
from typing import Union, List, Tuple

from PIL import Image, ImageTk

from base import BaseWrapper, check_name
from ui_utils import create_label_with_entry_by_grid
from utils import set_entry_value, Binder


@check_name
class ArticleOperationFrameWrapper(BaseWrapper):
    """文章操作区域"""
    name = 'article_operation_frame_wrapper'

    def __init__(self, parent: BaseWrapper):
        super().__init__(parent)

    def create(self):
        # 文章操作区域
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side='top', fill='x', expand=False)

    def bind(self):
        pass


@check_name
class ArticleContentFrameWrapper(BaseWrapper):
    """文章操作区域"""
    name = 'article_content_frame_wrapper'

    def __init__(self, parent: BaseWrapper):
        super().__init__(parent)
        self.add_article_btn: tk.Button | None = None

    def create(self):
        # 文章操作区域
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side='top', fill='both', expand=True)

        # 新增文章按钮
        self.add_article_btn = ttk.Button(self.widget, text="新增文章")
        self.add_article_btn.pack(side='left', fill='x', expand=False)
        name = f'{self.name}-add_article_btn'
        self.sub_widgets[name] = self.add_article_btn

        # 新增文章按钮
        self.add_article_btn = ttk.Button(self.widget, text="新增文章")
        self.add_article_btn.pack(side='left', fill='x', expand=False)
        name = f'{self.name}-add_article_btn'
        self.sub_widgets[name] = self.add_article_btn

        # 新增文章按钮
        self.add_article_btn = ttk.Button(self.widget, text="新增文章")
        self.add_article_btn.pack(side='left', fill='x', expand=False)
        name = f'{self.name}-add_article_btn'
        self.sub_widgets[name] = self.add_article_btn

        # 新增文章按钮
        self.add_article_btn = ttk.Button(self.widget, text="新增文章")
        self.add_article_btn.pack(side='left', fill='x', expand=False)
        name = f'{self.name}-add_article_btn'
        self.sub_widgets[name] = self.add_article_btn

        # 新增文章按钮
        self.add_article_btn = ttk.Button(self.widget, text="新增文章")
        self.add_article_btn.pack(side='left', fill='x', expand=False)
        name = f'{self.name}-add_article_btn'
        self.sub_widgets[name] = self.add_article_btn

    def bind(self):
        pass
