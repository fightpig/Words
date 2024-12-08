import tkinter as tk
import random
from threading import Timer
from tkinter import ttk, messagebox
from typing import Union, List, Tuple

from PIL import Image, ImageTk

from base import BaseWrapper, check_name
from ui_utils import create_label_with_entry_by_grid
from utils import set_entry_value, Binder, extract_words


@check_name
class WordOperationFrameWrapper(BaseWrapper):
    """单词操作区域"""

    name = "word_operation_frame_wrapper"

    def __init__(self, parent: BaseWrapper):
        self.stop_continuous_play_flag = None  # TODO
        self.continuous_play_btn: tk.Button | None = None
        self.stop_play_btn: tk.Button | None = None
        self.autoplay_btn: tk.Button | None = None
        self.episode_option_name_combobox: ttk.Combobox | None = None
        self.episode_option_value_entry: tk.Entry | None = None
        self.loop_interval_entry: tk.Entry | None = None
        self.loop_interval_label: tk.Label | None = None
        self.loop_cn_entry: tk.Entry | None = None
        self.loop_cn_label: tk.Label | None = None
        self.play_interval_entry: tk.Entry | None = None
        self.play_interval_label: tk.Label | None = None
        self.wordbook_combobox = None
        self.add_article_btn: tk.Button | None = None
        self.setting_btn = None

        super().__init__(parent)

    def _create_wordbook_combobox(self, frames: List[tk.Frame]):
        try:
            name = f"{self.name}-wordbook_combobox"
            self.wordbook_combobox = ttk.Combobox(
                frames[0], values=self.book.list_all_book_names(), height=10, name=name
            )
            self.wordbook_combobox.pack(side="left")
            self.sub_widgets[name] = self.wordbook_combobox
        except Exception:  # noqa
            messagebox.showerror("错误", "列出单词书出错")

    def _create_param_setting(self, frames: List[tk.Frame]):

        # 第2列：每集单词数/分钟数下拉框和输入框
        name = f"{self.name}-episode_option_name_combobox"
        values = ["每集单词数", "每集分钟数"]
        self.episode_option_name_combobox = ttk.Combobox(
            frames[1], values=values, width=10, name=name
        )
        self.episode_option_name_combobox.grid(
            row=0, column=0, padx=5, pady=5, sticky="ew"
        )
        self.episode_option_name_combobox.current(
            values.index(self.params.get("episode_option_name"))
        )  # 设置默认值
        self.sub_widgets[name] = self.episode_option_name_combobox
        name = f"{self.name}-episode_option_value_entry"
        self.episode_option_value_entry = ttk.Entry(frames[1], name=name, width=5)
        self.episode_option_value_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )
        set_entry_value(
            self.episode_option_value_entry, self.params.get("episode_option_value")
        )  # 设置默认值
        self.sub_widgets[name] = self.episode_option_value_entry

        # 第2列：播放间隔(秒)输入框、循环次数输入框、循环间隔(秒)输入框
        self.play_interval_label, self.play_interval_entry = (
            create_label_with_entry_by_grid(
                frames[1],
                l_text="播放间隔(秒):",
                lg_row=0,
                lg_column=2,
                lg_padx=5,
                lg_pady=5,
                lg_sticky="w",
                eg_row=0,
                eg_column=3,
                eg_padx=5,
                eg_pady=5,
                eg_sticky="w",
                e_default_value=self.params.get("play_interval"),
            )
        )
        name = f"{self.name}-play_interval_entry"
        self.sub_widgets[name] = self.play_interval_entry

        self.loop_cn_label = ttk.Label(frames[1], text="循环次数:")
        self.loop_cn_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        name = f"{self.name}-loop_cn_entry"
        self.loop_cn_entry = ttk.Entry(frames[1], name=name, width=5)
        self.loop_cn_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        set_entry_value(self.loop_cn_entry, self.params.get("loop_cn"))  # 设置默认值
        self.sub_widgets[name] = self.loop_cn_entry

        self.loop_interval_label = ttk.Label(frames[1], text="循环间隔(秒):")
        self.loop_interval_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        name = f"{self.name}-loop_interval_entry"
        self.loop_interval_entry = ttk.Entry(frames[1], name=name, width=5)
        self.loop_interval_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        set_entry_value(
            self.loop_interval_entry, self.params.get("loop_interval")
        )  # 设置默认值
        self.sub_widgets[name] = self.loop_interval_entry

        # 第2列：设置按键
        name = f"{self.name}-setting_btn"
        self.setting_btn = ttk.Button(frames[1], text="设置", name=name)
        self.setting_btn.grid(row=0, column=4, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.sub_widgets[name] = self.setting_btn

    def _create_4_btn(self, frames: List[tk.Frame]):
        # 第3列：正序、倒序列、自动播放、连续播放、停止播放、开始录制
        name = f"{self.name}-order_btn"
        self.order_btn = ttk.Button(frames[2], text="正序", name=name)
        self.order_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = self.order_btn
        name = f"{self.name}-autoplay_btn"
        self.autoplay_btn = ttk.Button(frames[2], text="自动播放", name=name)
        self.autoplay_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = self.autoplay_btn
        name = f"{self.name}-continuous_play_btn"
        self.continuous_play_btn = ttk.Button(frames[2], text="连续播放", name=name)
        self.continuous_play_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = self.continuous_play_btn

        name = f"{self.name}-random-order_btn"
        self.random_order_btn = ttk.Button(frames[2], text="乱序", name=name)
        self.random_order_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = self.random_order_btn
        name = f"{self.name}-stop_play_btn"
        self.stop_play_btn = ttk.Button(frames[2], text="停止播放", name=name)
        self.stop_play_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = self.stop_play_btn
        name = f"{self.name}-record_btn"
        self.record_btn = ttk.Button(frames[2], text="开始录制", name=name)
        self.record_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = self.record_btn

    def _create_search_add_btn(self, frames: List[tk.Frame]):
        name = f"{self.name}-search_word_entry"
        search_word_entry = ttk.Entry(frames[3], name=name, width=10)
        search_word_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = search_word_entry

        name = f"{self.name}-search_word_btn"
        search_word_btn = ttk.Button(frames[3], text="搜索单词", name=name, width=10)
        search_word_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.sub_widgets[name] = search_word_btn

        name = f"{self.name}-add_btn"
        self.add_article_btn = ttk.Button(
            frames[3], text="新增文章", name=name, width=10
        )
        # 将column参数设置为1，并将rowspan设置为2，这样按钮就会在第二列，占据两行
        self.add_article_btn.grid(
            row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew"
        )
        self.sub_widgets[name] = self.add_article_btn

    def create(self):
        # 单词操作区域
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side="top", fill="x", expand=False)

        frames = list()
        for _ in range(4):
            frame = ttk.Frame(self.widget)
            frame.pack(side="left", fill="both", expand=True)
            frames.append(frame)

        # 第1列：单词书下拉框
        self._create_wordbook_combobox(frames)
        sep1 = ttk.Separator(frames[0], orient="vertical")
        sep1.pack(side="left", fill="both", expand=False, padx=5, pady=5)

        # 第2列：每集单词数/分钟数下拉框和输入框
        # 第2列：播放间隔(秒)输入框、循环次数输入框、循环间隔(秒)输入框
        self._create_param_setting(frames)
        sep2 = ttk.Separator(frames[1], orient="vertical")
        sep2.grid(row=0, column=5, rowspan=2, padx=5, pady=5, sticky="nsew")

        # 第3列：自动播放、连续播放、停止播放、开始录制
        self._create_4_btn(frames)
        sep3 = ttk.Separator(frames[2], orient="vertical")
        sep3.grid(row=0, column=5, rowspan=2, padx=5, pady=5, sticky="nsew")

        # 第4列
        self._create_search_add_btn(frames)

        # 设置分隔线为虚线样式
        style = ttk.Style()
        style.configure("My.TSeparator", relief="sunken")
        for sep in [sep1, sep2, sep3]:
            sep.configure(style="My.TSeparator")

    def bind(self):
        name = f"{self.name}-wordbook_combobox"
        Binder.combobox_select(self.sub_widgets[name], self.on_combobox_select)
        Binder.click(self.setting_btn, self.on_click_setting_btn)
        Binder.click(self.continuous_play_btn, self.on_click_continuous_play_btn)
        Binder.click(self.stop_play_btn, self.on_click_stop_play_btn)
        Binder.click(self.record_btn, self.on_record_btn)
        Binder.click(self.add_article_btn, self.on_add_article_btn)
        Binder.click(self.order_btn, self.on_order_btn)
        Binder.click(self.random_order_btn, self.on_random_order_btn)

    def center_window(self, window):  # noqa
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry("{}x{}+{}+{}".format(width, height, x, y))

    def on_order_btn(self, event: tk.Event | None = None):
        word_content_frame: WordContentFrameWrapper = self.get_wrapper(
            WordContentFrameWrapper.name
        )  # noqa
        self.generate_word_listbox(
            self.book.cur_book_name, word_content_frame.word_listbox
        )

    def on_random_order_btn(self, event: tk.Event | None = None):
        word_content_frame: WordContentFrameWrapper = self.get_wrapper(
            WordContentFrameWrapper.name
        )  # noqa
        self.generate_word_listbox(
            self.book.cur_book_name, word_content_frame.word_listbox, to_random=True
        )

    def on_add_article_btn(self, event: tk.Event | None = None):
        # 创建一个Toplevel窗口
        input_window = tk.Toplevel(self.get_root_wrapper().widget)
        input_window.title("输入框")

        # 创建一个Label组件
        label = tk.Label(input_window, text="请输入一些文本:")
        label.pack(padx=10, pady=10)

        # 创建一个Text组件
        text = tk.Text(input_window, height=30, width=80)
        text.pack(padx=10, pady=10)

        # 创建一个Button组件，点击后获取Text中的文本并关闭窗口
        def on_confirm():
            new_article = text.get("1.0", tk.END)
            print("用户输入的内容是:\n", new_article)
            new_words = extract_words(new_article)
            print(new_words)
            input_window.destroy()  # 关闭Toplevel窗口
            self.show_word_editor(new_words)

        confirm_button = tk.Button(input_window, text="确认", command=on_confirm)
        confirm_button.pack(pady=5)

        # 调用函数使窗口居中
        self.center_window(input_window)

    def show_word_editor(self, words):
        editor_window = tk.Toplevel(self.get_root_wrapper().widget)
        editor_window.title("Word Editor")

        # 设置弹窗的大小
        editor_window.geometry("800x600")

        # 创建一个滚动框架
        frame = ttk.Frame(editor_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # 创建一个滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建一个画布，用于放置单词输入框
        canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 将滚动条的命令设置为画布的yview
        scrollbar.config(command=canvas.yview)

        # 创建一个容器用于放置单词输入框
        container = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=container, anchor="nw")

        # 存储输入框组件的字典
        entry_widgets = []

        # 创建单词输入框，每行15个
        for index, word in enumerate(words):
            row = index // 5
            col = index % 5
            entry = tk.Entry(container)
            entry.insert(0, word)
            entry.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            entry_widgets.append(entry)

        # 创建底部按钮和输入框的容器
        bottom_frame = ttk.Frame(editor_window)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建标签和输入框
        name_label = ttk.Label(bottom_frame, text="保存名字:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = tk.Entry(bottom_frame)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 创建“取消”和“保存”按钮
        cancel_button = tk.Button(
            bottom_frame, text="取消", command=editor_window.destroy
        )
        cancel_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        save_button = tk.Button(
            bottom_frame,
            text="保存",
            command=lambda: self.save_changes(entry_widgets, name_entry.get()),
        )
        save_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # 调用居中函数
        self.center_window(editor_window)

    def save_changes(self, entry_widgets, name):
        modified_words = [entry.get() for entry in entry_widgets]
        print(f"Name: {name}")
        print("Modified words:", modified_words)
        self.book.save_to_word_book(words=modified_words, word_book_name=name)

    def on_record_btn(self, event: tk.Event):
        if self.book.cur_book_name is None:
            messagebox.showerror("错误", "请先选择一本单词书")
            return

        wcf: WordContentFrameWrapper = self.get_word_content_frame_wrapper()  # noqa
        # print(f"Word content frame: offset: ({wcf.video_offset_x}, {wcf.video_offset_y})"
        #       f"size: ({wcf.video_width}, {wcf.video_height})")

        self.params["video_offset_x"] = wcf.video_offset_x
        self.params["video_offset_y"] = wcf.video_offset_y
        self.params["video_width"] = wcf.video_width
        self.params["video_height"] = wcf.video_height
        self.recorder_helper.auto_record(
            self.params, self.get_wrapper("root_wrapper"), self.book
        )  # noqa

        # w, h = self.get_widget_size(wcf.widget)
        # canvas = tk.Canvas(wcf.widget, width=w, height=h)
        # canvas.pack()
        # # 在Canvas的四个角处绘制红色直角线
        # draw_corners(canvas, w, h, line_length=20)

    def on_combobox_select(self, event: tk.Event):
        """选择单词书，列出所有单词，插入到左侧内容栏中"""
        name = f"{self.name}-wordbook_combobox"
        selected_book = self.sub_widgets[name].get()
        print("Selected:", selected_book)
        word_content_frame: WordContentFrameWrapper = self.get_wrapper(
            WordContentFrameWrapper.name
        )  # noqa
        self.generate_word_listbox(selected_book, word_content_frame.word_listbox)

    def on_click_setting_btn(self, event: tk.Event):
        """
        按第2列：每集单词数/分钟数下拉框和输入框、播放间隔(秒)输入框、循环次数输入框、循环间隔(秒)输入框的设置确定按钮
        """
        self.params.update(
            episode_option_name=self.episode_option_name_combobox.get(),
            episode_option_value=self.episode_option_value_entry.get(),
            play_interval=self.play_interval_entry.get(),
            loop_cn=self.loop_cn_entry.get(),
            loop_interval=self.loop_interval_entry.get(),
        )

    def on_click_continuous_play_btn(self, event: tk.Event | None = None):
        """
        将单词的循环次数变成列表，整个单词也是列表，然后循环单词列表
        """

        def play_word(idx_):
            if self.stop_continuous_play_flag or idx_ >= len(word_idx_list):
                return
            word_idx, interval = word_idx_list[idx_]
            # 更新界面显示单词含义
            self.select_word(word_idx, word_content_frame.word_listbox)
            word_content_frame.widget.update_idletasks()  # 强制更新界面
            word_content_frame.widget.after(interval * 1000, play_word, idx_ + 1)

        if self.book.cur_book_name is None:
            messagebox.showerror("错误", "请先选择一本单词书")
            return

        self.stop_continuous_play_flag = False
        s_idx = self.book.cur_word_idxes[self.book.cur_my_word.word]
        e_idx = len(self.book.cur_word_idxes)
        word_content_frame: WordContentFrameWrapper = self.get_wrapper(
            WordContentFrameWrapper.name
        )  # noqa

        word_idx_list = list()
        for idx in range(s_idx, e_idx + 1):
            for _ in range(self.params.get_loop_cn() - 1):
                word_idx_list.append((idx, self.params.get_loop_interval()))
            word_idx_list.append((idx, self.params.get_play_interval()))
        play_word(0)

    def on_click_stop_play_btn(self, event: tk.Event | None = None):
        self.stop_continuous_play_flag = True

    def generate_word_listbox(
        self, selected_book_name: str, word_listbox: tk.Listbox, to_random=False
    ):
        """
        1 清空单词列表框
        2 获取单词书的所有单词插入到列表中
        3 选中第一个单词
        """
        word_listbox.delete(0, tk.END)  # 清空列表框
        self.book.list_all_words(selected_book_name)

        # 添加单词到列表框
        idxes = list(self.book.cur_idx_words.keys())
        random.shuffle(idxes) if to_random else None
        [word_listbox.insert(tk.END, self.book.cur_idx_words[idx]) for idx in idxes]

        self.select_word(0, word_listbox)  # 选中第一个单词

    def select_word(self, word_idx: int, word_listbox: tk.Listbox):
        """触发选中左侧单词列表中的单词"""
        # 选中单词
        word_listbox.selection_clear(0, tk.END)
        word_listbox.selection_set(word_idx)
        word_listbox.activate(word_idx)
        word_listbox.event_generate("<<ListboxSelect>>")

        self.book.cur_my_word = self.book.get_my_word(word_idx)


@check_name
class WordContentFrameWrapper(BaseWrapper):
    """单词显示区域"""

    name = "word_content_frame_wrapper"

    def __init__(self, parent: Union["BaseWrapper", None] = None):
        self.word_show_frame: tk.Frame | None = None
        self.video_height = None
        self.video_width = None
        self.video_offset_y = None
        self.video_offset_x = None
        self.m_content_frame: tk.Frame | None = None
        self.words = ["apple", "banana", "cherry", "date", "fig"]
        self.to_size = (42, 42)
        self.cur_word_idx = 0  # 当前单词的索引
        self.word_list_frame: tk.Widget | None = None
        self.word_listbox: tk.Listbox | None = None
        self.word_label: tk.Label | None = None
        self.phonetic_label: tk.Label | None = None
        self.meaning_label: tk.Label | None = None

        self.timer = None

        super().__init__(parent)

    def create(self):
        # 单词显示区域
        self.widget = ttk.Frame(self.parent.widget, name=self.name)
        self.widget.pack(side="top", fill="both", expand=True)

        # 单词列表
        name = f"{self.name}-word_listbox"
        self.word_listbox = tk.Listbox(
            self.widget, width=15, height=15, font=("Helvetica", 15)
        )
        self.word_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sub_widgets[name] = self.word_listbox

        # 创建Scrollbar控件
        scrollbar = tk.Scrollbar(self.widget, orient=tk.VERTICAL, width=25)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # 配置Listbox和Scrollbar
        self.word_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.word_listbox.yview)

        # # 添加单词列表和内容显示区域的分隔线
        # # TODO，加上滚动条
        # word_list_sep = ttk.Separator(self.widget, orient='vertical')
        # word_list_sep.pack(side='left', fill='y', padx=2)

        # 单词内容显示区域
        name = f"{self.name}-word_show_frame"
        self.word_show_frame = ttk.Frame(self.widget, name=name)
        self.word_show_frame.pack(side="left", fill="both", expand=True)
        self.sub_widgets[name] = self.word_show_frame

        # w, h = self.get_widget_size(word_content_frame)
        # canvas = tk.Canvas(word_content_frame, width=w, height=h)
        # canvas.pack()
        # # 在Canvas的四个角处绘制红色直角线
        # draw_corners(canvas, w, h, line_length=20)

        self.get_wrapper("root_wrapper").widget.update()
        width = self.word_show_frame.winfo_width()
        button_width = int(width * 0.05)
        l_btn_frame = ttk.Frame(self.word_show_frame, width=button_width)
        l_btn_frame.pack(side="left", fill="y")
        self.m_content_frame = ttk.Frame(
            self.word_show_frame, width=width - 2 * button_width
        )
        self.m_content_frame.pack(side="left", fill="both", expand=True)
        r_btn_frame = ttk.Frame(self.word_show_frame, width=button_width)
        r_btn_frame.pack(side="right", fill="y")

        # 单词内容显示
        name = f"{self.name}-word_label"
        self.word_label = ttk.Label(
            self.m_content_frame, text="", font=("Helvetica", 20), name=name
        )
        self.word_label.pack(pady=20, anchor="center")
        self.sub_widgets[name] = self.word_label

        name = f"{self.name}-phonetic_label"
        self.phonetic_label = ttk.Label(
            self.m_content_frame, text="", font=("Helvetica", 16), name=name
        )
        self.phonetic_label.pack(pady=20, anchor="center")
        self.sub_widgets[name] = self.phonetic_label

        name = f"{self.name}-meaning_label"
        self.meaning_label = ttk.Label(
            self.m_content_frame, text="", font=("Helvetica", 14), name=name
        )
        self.meaning_label.pack(pady=20, anchor="center")
        self.sub_widgets[name] = self.meaning_label
        # 设置垂直居中
        # for label in [self.word_label, self.phonetic_label, self.meaning_label]:
        #     label.pack_configure(pady=(100, 10))  # 垂直居中，可以调整pady值

        # 箭头按钮
        prev_word_img = self.resize_img("../sources/icons/prev.png")
        name = f"{self.name}-prev_word_btn"
        prev_word_btn = ttk.Button(
            l_btn_frame, text="<<", image=prev_word_img, command=self.prev_word, width=5
        )
        prev_word_btn.pack(side="left", padx=10)
        self.sub_widgets[name] = prev_word_btn

        next_word_img = self.resize_img("../sources/icons/next.png")
        name = f"{self.name}-next_word_btn"
        next_word_btn = ttk.Button(
            r_btn_frame, text=">>", image=next_word_img, command=self.next_word, width=5
        )
        next_word_btn.pack(side="right", padx=10)
        self.sub_widgets[name] = next_word_btn

    def bind(self):
        Binder.listbox_select(self.word_listbox, func=self.on_listbox_select)
        # TODO
        # Binder.configure(self.get_wrapper('root_wrapper').widget, self.on_move, self.widget)

    def on_move(self, event, *args):
        # 如果存在定时器，则取消它（防抖动）
        if self.timer is not None:
            self.timer.cancel()
        # 设置一个新的定时器，在一段时间后执行获取坐标的操作
        self.timer = Timer(0.5, self.get_position)  # 等待0.5秒
        self.timer.start()

    def get_position(self):
        x = self.get_wrapper("root_wrapper").widget.winfo_x()
        y = self.get_wrapper("root_wrapper").widget.winfo_y()

        offset_x = 370
        offset_h = 230

        self.video_offset_x = x + offset_x
        self.video_offset_y = y + offset_h

        self.video_width = (
            self.get_word_content_frame_wrapper().word_show_frame.winfo_width() - 20
        )
        self.video_height = (
            self.get_word_content_frame_wrapper().word_show_frame.winfo_height() - 20
        )

        print(
            f"Word content frame: offset: ({self.video_offset_x}, {self.video_offset_y})"
            f"size: ({self.video_width}, {self.video_height})"
        )

    def display_word(self, word_idx: int):
        word = self.word_listbox.get(word_idx)
        my_word = self.book.get_my_word(word)
        self.book.cur_my_word = my_word
        self.word_label.config(text="")
        self.word_label.config(text=word, foreground="blue")

        phonetic = ""
        if my_word.default_phonetic:
            phonetic = my_word.default_phonetic
        else:
            us_phonetic = my_word.us_phonetic
            if us_phonetic:
                us_phonetic = (
                    us_phonetic if "[" in us_phonetic else f"[{us_phonetic.strip()}"
                )
                us_phonetic = (
                    us_phonetic if "]" in us_phonetic else f"{us_phonetic.strip()}]"
                )
                us_phonetic = (
                    us_phonetic if "美" in us_phonetic else f"美 {us_phonetic.strip()}"
                )
                phonetic = us_phonetic

            uk_phonetic = my_word.uk_phonetic
            if uk_phonetic:
                uk_phonetic = (
                    uk_phonetic if "[" in uk_phonetic else f"[{uk_phonetic.strip()}"
                )
                uk_phonetic = (
                    uk_phonetic if "]" in uk_phonetic else f"{uk_phonetic.strip()}]"
                )
                uk_phonetic = (
                    uk_phonetic if "英" in uk_phonetic else f"英 {uk_phonetic.strip()}"
                )
                phonetic += "  " + uk_phonetic if phonetic else uk_phonetic
        self.phonetic_label.config(text="")
        self.phonetic_label.config(text=phonetic, foreground="green")

        if my_word.meaning_dict:
            self.meaning_label.config(text="")
            meaning = self.book.get_word_meaning(my_word)
            if meaning:
                tmp = list()
                for k, v in meaning.items():
                    tmp.append(f"{k}  {v[:32]}")
                    v = v[32:]
                    while len(v) >= 32:
                        tmp.append(" " * len(k) + "  " + v[:32])
                        v = v[32:]
                    if len(v) > 0:
                        tmp.append(" " * len(k) + "  " + v)
                meaning = "\n".join(tmp)
            else:
                meaning = ""
            self.meaning_label.config(text=meaning, foreground="purple")

    def on_listbox_select(self, event: tk.Event):
        """当单词列表的某个单词被选中时，在右侧显示内容，并且播放MP3"""
        selected_word_idx = self.word_listbox.curselection()
        if not selected_word_idx:
            return

        self.display_word(selected_word_idx)
        print(f"点击单词：{self.book.cur_my_word.word}")
        audio_path = self.book.get_word_audio_paths(self.book.cur_my_word)
        (
            self.audio.play(audio_path[0])
            if audio_path
            else print(f"{self.book.cur_my_word.word}没有mp3")
        )

    def get_selected_word(self) -> Tuple[int | None, str | None]:
        """获取当前被选中的单词"""
        try:
            selected_index = self.word_listbox.curselection()[0]
            selected_word = self.word_listbox.get(selected_index)
            return selected_index, selected_word
        except IndexError:
            return None, None

    def resize_img(self, img_path):
        img = Image.open(img_path)
        img = img.resize(self.to_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def prev_word(self):
        if self.book.cur_book_name is None:
            return
        cur_word_idx = self.book.cur_my_word.id
        if cur_word_idx >= 1:
            cur_word_idx -= 1
            self.get_wrapper(WordOperationFrameWrapper.name).select_word(
                cur_word_idx, self.word_listbox
            )

    def next_word(self):
        if self.book.cur_book_name is None:
            return
        cur_word_idx = self.book.cur_my_word.id
        if cur_word_idx < len(self.book.cur_idx_words) - 1:
            cur_word_idx += 1
            self.get_wrapper(WordOperationFrameWrapper.name).select_word(
                cur_word_idx, self.word_listbox
            )
