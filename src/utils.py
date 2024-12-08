import json
import logging.config
import os
import string
import threading
import time
import tkinter as tk
from pathlib import Path
from typing import List, Tuple, Any, Callable, Literal

import pygame
import requests
import yaml
from mutagen.mp3 import MP3

HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"  # noqa
}

# 读取YAML配置文件
with open("../conf/logging.yaml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

# 获取配置好的logger
my_logger = logging.getLogger("my_logger")


def my_print(msg: Any, to_print: bool = True):
    my_logger.info(msg) if to_print else None


def download_file(
    save_path: str | Path, url: str, headers: dict = None
) -> Tuple[bool, int, Exception]:
    ex = None
    ret = False
    status_code = 200

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            os.makedirs(Path(save_path).parent, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)
            ret = True
    except Exception as e:
        ex = e

    return ret, status_code, ex


def download_audio_file(
    save_dir_path: str | Path,
    source: str,
    kind: str,
    word: str,
    url: str | None = None,
    using_baidu_when_fail: bool = True,
    to_print=False,
    refetch_audio=False,
) -> Tuple[bool, str]:
    """
    save_dir_path: 音频库根目录
    source: bing | sogou | baidu
    kind: us | uk
    """

    def _f(source_, url_, save_path_: str):

        ret_, status_code, ex = download_file(save_path, url_, headers=HEADERS)
        if ret_:
            my_print(f"{Path(save_path_).name} 已保存, source: {source_}", to_print)
            return True
        else:
            my_print(
                f"Fail to download {word}'s audio: {url_}, source: {source_}, status code: {status_code}, ex: {ex}",
                to_print,
            )
            return False

    save_path = f"{save_dir_path}/{source}/{kind}/{word[0].lower()}/{word}.mp3"
    if refetch_audio is False:
        if Path(save_path).exists():  # TODO
            print(f"{save_path}已存在")
            return True, save_path
    if url:
        ret = _f(source, url, save_path)
        if ret:
            return True, save_path

    if using_baidu_when_fail:
        save_path = f"{save_dir_path}/baidu/{kind}/{word[0].lower()}/{word}.mp3"
        if refetch_audio is False:
            if Path(save_path).exists():  # TODO
                my_logger.info(f"{save_path}已存在")
                return True, save_path
        my_logger.info("Using baidu to download audio")
        url = (
            os.environ.get("baidu-us-audio-url")
            if kind == "us"
            else os.environ.get("baidu-uk-audio-url")
        ).format(text=word)
        ret = _f("baidu", url, save_path)
        if ret:
            return True, save_path
    return False, ""


def save_to_json_or_yaml(
    data: dict, save_path: str | Path, to_json: bool = True, to_print=False
):
    save_path = Path(save_path) if isinstance(save_path, str) else save_path
    os.makedirs(save_path.parent, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as file:
        if to_json:
            json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            yaml.safe_dump(data, file, indent=4, allow_unicode=True)
        print(f"Saved {save_path}") if to_print else None


def save_to_json(data: dict, save_path: str | Path, to_print=False):
    save_to_json_or_yaml(data, save_path, to_json=True, to_print=to_print)


def save_to_yaml(data: dict, save_path: str | Path, to_print=False):
    save_to_json_or_yaml(data, save_path, to_json=False, to_print=to_print)


def read_from_json_or_yaml(
    file_path: str | Path, from_json: bool = True
) -> dict:  # noqa
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file) if from_json else yaml.safe_load(file)


def read_from_json(file_path: str | Path) -> dict:  # noqa
    return read_from_json_or_yaml(file_path, from_json=True)


def read_from_yaml(file_path: str | Path) -> dict:  # noqa
    return read_from_json_or_yaml(file_path, from_json=False)


def read_file(file_path: str | Path) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


class RecorderHelper:
    # from ui import Root
    # from book import Book
    # from configuration import Params

    def __init__(self, save_dir_path):
        from media import Recorder

        self.save_path = save_dir_path
        pygame.mixer.init()
        self.video_recorder: Recorder | None = None

    def auto_record(self, params: "Params", root: "Root", book: "Book"):  # noqa
        from plan import RecordPlan
        from media import Recorder
        from main_ui import WordContentFrameWrapper, WordOperationFrameWrapper

        def _record(idx: int):
            nonlocal recorder
            if idx >= len(plans):
                return

            s_word_obj, e_word_obj, duration, num = plans[idx]
            if recorder is None:
                recorder = Recorder(
                    self.save_path,
                    f"{video_name}-part{idx + 1}-num{num}-loop{loop_cn}",
                    video_screen_offset=(
                        params["video_offset_x"],
                        params["video_offset_y"],
                    ),
                    video_screen_size=(params["video_width"], params["video_height"]),
                )
            recorder.start()

            # 选中单词
            word_content_frame: WordContentFrameWrapper = root.get_wrapper(
                "word_content_frame_wrapper"
            )
            book.select_word(s_word_obj.id, word_content_frame.word_listbox)

            # 触发连续播放
            operation_frame: WordOperationFrameWrapper = root.get_wrapper(
                "word_operation_frame_wrapper"
            )
            operation_frame.on_click_continuous_play_btn()

            def check_word():
                nonlocal recorder
                cur_word_idx, cur_word = word_content_frame.get_selected_word()
                if cur_word == e_word_obj.word:
                    # TODO 有bug，暂停回来，就从下一个单词开始
                    operation_frame.on_click_stop_play_btn()
                    time.sleep(3)
                    recorder.stop_record()
                    # 这是耗时操作，得放到队列中，一个一个有序的执行，没执行完，用户要关app，弹出提示
                    threading.Thread(target=recorder.compose).start()
                    recorder = None
                    print("录制完成，休息3秒")
                    time.sleep(3)
                    root.widget.after(
                        0, _record, idx + 1
                    )  # Schedule the next recording
                else:
                    root.widget.after(check_interval, check_word)

            # Schedule the first check
            check_interval = 100  # Check every 1000 milliseconds (1 second)
            root.widget.after(check_interval, check_word)

        episode_option_name = params["episode_option_name"]
        episode_option_value = params["episode_option_value"]

        video_name = book.cur_book_name
        play_interval = params.get_play_interval()
        loop_cn = params.get_loop_cn()
        loop_interval = params.get_loop_interval()

        s_word_idx = params.get_selected_word_idx()
        e_word_idx = max(book.cur_idx_words.keys())

        plans = RecordPlan(
            book,
            s_word_idx,
            e_word_idx,
            episode_option_name,
            episode_option_value,
            loop_cn,
        ).plan()
        *_, num = plans[0]
        os.makedirs(self.save_path, exist_ok=True)
        recorder: Recorder | None = None
        _record(0)

    # def start_recording(self, root):
    #     self.video_recorder = Recorder(self.save_path, self.save_name)
    #     self.video_recorder.start()
    #     self.video_recorder.start_record()
    #
    # def stop_recording(self):
    #     self.video_recorder.stop_record_and_compose()

    @staticmethod
    def load_sound(file_name):
        return pygame.mixer.Sound(file_name) if file_name else None

    # 播放MP3文件
    @staticmethod
    def play_sound(sound):
        sound.play()


class Binder:
    @staticmethod
    def bind(action_name: str, widget: tk.Widget, func: Callable, *args):
        if len(args) > 0:
            widget.bind(f"{action_name}", lambda event: func(event, *args))
        else:
            widget.bind(f"{action_name}", lambda event: func(event))

    @classmethod
    def combobox_select(cls, widget: tk.Widget, func: Callable):
        """下拉框下拉操作"""
        cls.bind("<<ComboboxSelected>>", widget, func)

    @classmethod
    def listbox_select(cls, widget: tk.Widget, func: Callable):
        """列表选中操作"""
        cls.bind("<<ListboxSelect>>", widget, func)

    @classmethod
    def click(cls, widget: tk.Widget, func: Callable):
        """列表选中操作"""
        cls.bind("<Button-1>", widget, func)

    @classmethod
    def configure(cls, widget: tk.Widget, func: Callable, *args):
        """获取widget的相关信息"""
        cls.bind("<Configure>", widget, func, *args)


def toggle_btn_color(btn_ls: List[tk.Button], color="green"):
    # TODO
    # 设置被点击按钮的背景颜色为绿色
    # btn_ls[0].config(bg=color)
    # 设置另一个按钮的背景颜色为默认颜色（通常是白色或灰色）
    # [btn.config(bg='SystemButtonFace') for btn in btn_ls[1:]]
    pass


def set_entry_value(
    entry: tk.Entry,
    value: str | int,
    justify: Literal["left", "center", "right"] = "right",
):
    entry.insert(0, str(value))
    entry.config(justify=justify)


def extract_words(text):
    # 定义一个翻译表，将所有标点符号映射为None，但保留连字符
    translator = str.maketrans("", "", string.punctuation.replace("-", ""))

    # 使用翻译表去除文本中的标点符号，但保留连字符
    text_without_punctuation = text.translate(translator)

    # 使用空格将文本分割成单词列表
    words = text_without_punctuation.split()

    return words


def get_mp3_duration(filename):
    """返回mp3时长"""
    audio = MP3(filename)
    return audio.info.length  # 返回时长（秒）
