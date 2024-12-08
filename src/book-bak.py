import json
import os
import string
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import random
from tkinter import messagebox
import tkinter as tk
from typing import List, Dict, Union, Tuple, Self

import yaml
from icecream import ic
from pydantic import BaseModel

from src.configuration import Config, AudioKind, AudioSource

# from src.fetcher import Bing, Sogou
from src.utils import (
    save_to_json,
    save_to_yaml,
    read_from_json,
    read_from_yaml,
    read_file,
    download_audio_file,
)


class MyWord(BaseModel):
    word: str
    """单词"""
    idx: int | str | None = None
    """序号"""
    cur_book_name: str | None = None
    """当前所属单词书"""

    default_phonetic: str | None = None
    """默认音标"""
    us_phonetic: str | None = None
    """美式音标"""
    uk_phonetic: str | None = None
    """英式音标"""

    default_audio_url_dict: Dict[str, str] | None = dict()
    """默认读音链接
    {
        sogou: url,
        bing: url,
        baidu: url,
    }
    """
    us_audio_url_dict: Dict[str, str] | None = dict()
    """美式读音链接
    {
        sogou: url,
        bing: url,
        baidu: url,
    }
    """
    uk_audio_url_dict: Dict[str, str] | None = dict()
    """英式读音链接
    {
        sogou: url,
        bing: url,
        baidu: url,
    }
    """
    ai_audio_url_dict: Dict[str, str] | None = dict()
    """AI读音链接
    {
        sogou: url,
        bing: url,
        baidu: url,
    }
    """

    default_audio_path_dict: Dict[str, str | Path] | None = dict()
    """默认读音路径
    {
        nce: path,
        sogou: path,
        oxford5000: path,
    }
    """
    us_audio_path_dict: Dict[str, str | Path] | None = dict()
    """㺯式读音路径
    {
        nce: path,
        sogou: path,
        oxford5000: path,
    }
    """
    uk_audio_path_dict: Dict[str, str | Path] | None = dict()
    """美式读音路径
    {
        nce: path,
        sogou: path,
        oxford5000: path,
    }
    """
    ai_audio_path_dict: Dict[str, str | Path] | None = dict()
    """AI读音路径
    {
        nce: path,
        sogou: path,
        oxford5000: path,
    }
    """

    meaning_str: Dict[str, str] | None = dict()
    """
    中文含义:
        {

            Bing: 词性. 含义 \n词性. 含义,
            Sogou: 词性. 含义 \n词性. 含义,
        }
    """
    # part_of_speech_ls: List[str] | None = None
    # """词性"""
    meaning_dict: Dict[str, Dict[str, str]] | None = defaultdict(dict)
    """
    中文含义: 
        Bing: {
            词性: 含义,
            词性: 含义,
        },
        Sogou: {
            词性: 含义,
            词性: 含义,
        }
    """
    w_plural: str | None = None
    """复数"""
    w_third: str | None = None
    """三单"""
    w_ing: str | None = None
    """现在分词"""
    w_done: str | None = None
    """过去分词"""
    w_past: str | None = None
    """过去式"""

    sentence_num: int | None = None
    """例句数量"""
    sentence_dict: Dict[str, Dict[int | str, Dict[str, str]]] | None = defaultdict(
        lambda: defaultdict(lambda: defaultdict(str))
    )
    """
    例句:
    {
        Bing: {
            1: {en: xxx, cn: yyy},
            2: {en: xxx, cn: yyy},
        },
        Sogou: {
            1: {en: xxx, cn: yyy},
            2: {en: xxx, cn: yyy},
        },
    }
    """
    sentence_audio_url_dict: Dict[str, Dict[int | str, str | None]] | None = (
        defaultdict(dict)
    )
    """例句发音链接
    {
        Bing:{
            1: url,
            2: url,
        },
        Sogou:{
            1: url,
            2: url,
        },
    }
    """
    sentence_audio_path_dict: Dict[str, Dict[int | str, str]] | None = defaultdict(dict)
    """例句发音路径
    {
        Bing:{
            1: path,
            2: path,
        },
        Sogou:{
            1: path,
            2: path,
        },
    }
    """
    picture_num: int | None = None
    """例图数量"""
    picture_url_dict: Dict[str, List[str]] | None = defaultdict(list)
    """例图链接
    {
        Bing: [url, url],
        Sogou: [url, url],
    }
    """
    picture_path_dict: Dict[str, List[str]] | None = defaultdict(list)
    """例图路径
    {
        Bing: [url, url],
        Sogou: [url, url],
    }
    """
    level: str | None = None
    """
    >CET4 
    CET4 
    CET6 
    <CET6
    """
    oxford_level: str | None = None
    """
    A1: beginner
    A2: elementary
    B1: intermediate
    B2: upper intermediate
    C1: advanced ~ 托福94-114分, 雅思7-8分
    C2: proficient ~ 托福115分及以上，雅思8.5分及以上
    """

    def save_to_json(self, save_dir_path: str | Path, to_print=False):
        save_to_json(
            data=self.model_dump(),
            save_path=f"{save_dir_path}/{self.word}.json",
            to_print=to_print,
        )

    def save_to_yaml(self, save_dir_path: str | Path, to_print=False):
        save_to_yaml(
            data=self.model_dump(),
            save_path=f"{save_dir_path}/{self.word}.yaml",
            to_print=to_print,
        )

    def load_word_info(
        self,
        word: str | None = None,
        word_idx: int | None = None,
        cur_book_name: str | None = None,
    ) -> Self:
        """加载单词信息"""
        return self.load_word_info_with_download(
            word,
            word_idx,
            cur_book_name,
            auto_fetch_word_info=False,
            auto_download_audio=False,
        )

    def load_word_info_with_download(
        self,
        word: str,
        word_idx: int,
        cur_book_name: str,
        word_info_libs_dir_path: Path,
        sogou_word_info_libs_dir_path: Path,
        auto_fetch_word_info: bool = False,
        auto_download_audio: bool = False,
    ) -> Self:
        """加载单词信息，不存在时从网上爬取，并更新"""
        assert word or word_idx is not None
        # word = word if word else self.cur_idx_words.get(word_idx)
        # word_idx = word_idx if word_idx else self.cur_word_idxes.get(word)
        # cur_book_name = cur_book_name if cur_book_name else self.cur_book_name
        my_word = MyWord(word=word, cur_book_name=str(cur_book_name), idx=word_idx)
        word_json_path = self.word_info_path_dict.get(word)
        need_save = False

        if not word_json_path or not word_json_path.exists():
            # 下载单词信息
            need_save = True
            if auto_fetch_word_info:
                bing_my_word = Bing.fetch(word)
                sogou_my_word = Sogou.fetch(
                    word,
                    to_my_word=True,
                    save_json_path=(
                        sogou_word_info_libs_dir_path / f"{word}.json"
                        if sogou_word_info_libs_dir_path
                        else None
                    ),
                )
                my_word = MyWord.update_my_word(my_word, bing_my_word)
                my_word = MyWord.update_my_word(my_word, sogou_my_word)
        else:
            # 从本地json读取单词信息
            with open(word_json_path, "r", encoding="utf-8") as f:
                kvs = json.load(f)
                kvs.pop("id", None)
                kvs.pop("cur_book_name", None)
                my_word.__dict__.update(**kvs)

        if need_save:  # 保存json
            self.update_word_audio_paths(
                my_word
            )  # TODO，不需要写audio_path，每次启动时重新加载
            my_word.save_to_json(word_info_libs_dir_path / f"{word[0].lower()}")

        self.get_word_audio_path_with_download(
            my_word, auto_download_audio, auto_download_audio, check=True
        )
        return my_word

    def get_my_word(self, word_or_obj: str | Self) -> Self:
        return (
            word_or_obj
            if isinstance(word_or_obj, MyWord)
            else self.load_word_info(word_or_obj)
        )

    def get_word_audio_path_with_download(
        self,
        word_or_obj: str | Self,
        word_audio_path_dict: Dict[str, Dict[str, Dict[str, str]]],
        config: Dict[str, List[str]],
        word_audio_libs_dir_path,
        auto_download=True,
        using_baidu_when_fail=True,
        check=True,
    ) -> List[str]:
        """根据配置文件的优先级，从本地word-audio-libs库中依次寻找对应的音频"""
        my_word = self.get_my_word(word_or_obj)
        for kind in list(AudioKind):
            setattr(my_word, f"{kind}_audio_url_dict", word_audio_path_dict.get(kind))

        priority: List[Tuple[str, str]] = [
            (source, kind)
            # for source in self.config["priority"]["word-audio-libs"]["path"]
            # for kind in self.config["priority"]["word-audio-libs"]["path"].get(source)
            for source in config.keys()
            for kind in config[source]
        ]

        audio_path_dicts = {
            AudioKind.DEFAULT: my_word.default_audio_path_dict or dict(),
            AudioKind.US: my_word.us_audio_path_dict or dict(),
            AudioKind.UK: my_word.uk_audio_path_dict or dict(),
            AudioKind.AI: my_word.ai_audio_path_dict or dict(),
        }

        audio_paths = list()
        for source, kind in priority:
            audio_path = audio_path_dicts.get(kind).get(source)  # noqa
            if audio_path and Path(audio_path).exists():
                audio_paths.append(audio_path)
            elif auto_download:
                url = getattr(my_word, f"{kind}_audio_url_dict").get(source)
                ret, audio_path = download_audio_file(
                    word_audio_libs_dir_path,
                    source,
                    kind,
                    my_word.word,
                    url,
                    using_baidu_when_fail=using_baidu_when_fail,
                    refetch_audio=check,
                    to_print=True,
                )
                audio_paths.append(audio_path)
        return audio_paths

    def get_word_meaning(
        self, word_or_obj: str | Self, priority: List[str]
    ) -> Dict[str, str] | None:
        """根据配置文件的优先级，获取含义

        :param word_or_obj:
        :param priority:
            word-info-libs:
            - bing  # bing-网络.
            - nce
            - sogou
        """
        word_obj = self.get_my_word(word_or_obj)

        # priority: List[str] = [
        #     kind for kind in self.config["priority"]["word-info-libs"]
        # ]

        for kind in priority:
            key = None
            if len(kind.split("-")) == 2:
                kind, key = kind.split("-")
            meaning_dict: Dict[str, str] = word_obj.meaning_dict.get(kind)
            if meaning_dict:
                if key and key in meaning_dict:
                    return {key: meaning_dict.get(key)}
                return meaning_dict

    @staticmethod
    def read_from_json(json_path: str | Path) -> "MyWord":
        return MyWord(**read_from_json(json_path))

    @staticmethod
    def read_from_yaml(yaml_path: str | Path) -> "MyWord":
        return MyWord(**read_from_yaml(yaml_path))

    def to_txt(self, save_dir_path: Union[str, Path]) -> None:
        os.makedirs(save_dir_path, exist_ok=True)
        with open(f"{save_dir_path}/{self.word}.txt", "w", encoding="utf-8") as file:
            for attr_name in self.model_fields.keys():
                attr_value = getattr(self, attr_name)
                if attr_value is None:
                    attr_value = "__none__"
                elif isinstance(attr_value, (dict, list)):
                    attr_value = str(attr_value)
                elif isinstance(attr_value, Path):
                    attr_value = str(attr_value)
                file.write(f"# {attr_name}\n{attr_value}\n\n")

    @staticmethod
    def update_my_word(
        to_word_obj: "MyWord",
        from_word_obj: Union["MyWord", None],
        exclude_attrs=("id", "word", "cur_book_name"),
    ) -> "MyWord":
        if from_word_obj is None:
            return to_word_obj

        updated_word = to_word_obj.model_copy(deep=True)
        for attr, value in from_word_obj:
            if attr not in exclude_attrs and value is not None:
                current_value = getattr(updated_word, attr)
                if isinstance(value, defaultdict) and isinstance(
                    current_value, defaultdict
                ):
                    for k, v in value.items():
                        current_value[k] = v
                elif isinstance(value, dict) and isinstance(current_value, dict):
                    current_value.update(value)
                elif isinstance(value, list) and isinstance(current_value, list):
                    current_value.extend(value)
                else:
                    setattr(updated_word, attr, value)

        return updated_word


class Book:
    def __init__(
        self,
        book_dir_path="../sources/word-book",
        word_audio_libs_dir_path="../sources/word-audio-libs",
        word_info_libs_dir_path="../sources/word-info-libs",
        sogou_word_info_libs_dir_path="../sources/sogou-word-info-libs",
        config: Config | None = None,
        showerror_by_messagebox=True,
    ):
        self.showerror_by_messagebox = showerror_by_messagebox
        self.book_dir_path = Path(book_dir_path)
        self.word_audio_libs_dir_path = Path(word_audio_libs_dir_path)
        self.word_info_libs_dir_path = Path(word_info_libs_dir_path)
        self.sogou_word_info_libs_dir_path = Path(sogou_word_info_libs_dir_path)
        self.config = config if config else Config()

        # {909: 909}
        self.bookname_dirs = dict()  # noqa
        # {cook: 1}
        self.cur_word_idxes = dict()
        # {1: cook}
        self.cur_idx_words = dict()

        self.cur_book_name = None
        self.cur_word_obj: MyWord | None = None

        # [(nce, us), (nce, uk), (oxford5000, us), (oxford5000, uk)]
        self.priority: List[Tuple[str, str]] = list()

        # word_audio_path_dict[cook][us][oxford5000] = '../sources/word-audio-libs/oxford5000/us/c/cook.mp3'
        self.word_audio_path_dict: Dict[str, Dict[str, Dict[str, str]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(str))
        )
        self.word_info_path_dict: Dict[str, Path] = dict()

        self.list_all_word_audio_paths(
            self.word_audio_libs_dir_path, self.word_audio_path_dict
        )
        self.list_all_word_info_paths(
            self.word_info_libs_dir_path, self.word_info_path_dict
        )

    # def list_all_word_audio_paths(self):
    #     """加载所有单词音频的mp3/wav路径
    #     word_audio_path_dict[cook][us][oxford5000] = '../sources/word-audio-libs/oxford5000/us/c/cook.mp3'
    #     """
    #     list_all_word_audio_paths(
    #         self.word_audio_libs_dir_path, self.word_audio_path_dict
    #     )

    # def list_all_word_info_paths(self):
    #     """加载所有单词信息的json路径"""
    #     list_all_word_info_paths(self.word_info_libs_dir_path, self.word_info_path_dict)

    def list_all_book_names(self) -> List[str]:
        """单词书名列表"""
        try:
            for p in self.book_dir_path.iterdir():
                config = Config(p / "conf.yaml")
                self.bookname_dirs[str(config.get("name"))] = p.name
        except Exception as e:
            print(e)
            # (
            #     messagebox.showerror("错误", "列出单词书出错")
            #     if self.showerror_by_messagebox
            #     else None
            # )
            raise Exception("列出单词书出错")
        return list(self.bookname_dirs.keys())

    def list_all_words(self, book_name: str):
        """指定单词书的单词列表"""
        try:
            self.list_all_book_names()
            book_dir = self.bookname_dirs.get(book_name)
            config = read_from_yaml(self.book_dir_path / book_dir / "conf.yaml")
            self.config.update(**config)

            lines = read_file(
                f'{self.book_dir_path}/{book_dir}/{self.config.get("path")}'
            )
            words = [
                line.strip() for line in lines if self.parse_word_rule_1(line)
            ]  # TODO，读取方式
        except Exception as e:
            print(e)
            # if self.showerror_by_messagebox:
            #     messagebox.showerror("错误", f"无法打开单词书: {book_name}\n{e}")
            raise Exception(f"无法打开单词书: {book_name}")
        else:
            self.cur_book_name = book_name
            self.cur_word_idxes = {word: idx for idx, word in enumerate(words)}
            self.cur_idx_words = {idx: word for idx, word in enumerate(words)}

    def update_word_audio_paths(
        self,
        word_or_obj: str | MyWord,
        generate_ai_audio_when_no=False,  # TODO
    ) -> Tuple[int, MyWord]:

        def _f(kind_):
            nonlocal cn
            for source, audio_path in (
                self.word_audio_path_dict.get(word, dict()).get(kind, dict()).items()
            ):
                if audio_path and Path(audio_path).exists():
                    getattr(my_word, f"{kind_}_audio_path_dict").update(
                        {source: audio_path}
                    )
                    cn += 1

        word = word_or_obj.word if isinstance(word_or_obj, MyWord) else word_or_obj
        my_word = word_or_obj if isinstance(word_or_obj, MyWord) else MyWord(word=word)
        cn = 0

        for kind in list(AudioKind):  # us | uk | default | ai
            _f(kind)

        print(f"word: {word} have no audio") if cn == 0 else None
        return cn, my_word

    def generate_word_listbox(
        self, selected_book_name: str, word_listbox: tk.Listbox, to_random=False
    ):
        """
        1 清空单词列表框
        2 获取单词书的所有单词插入到列表中
        3 选中第一个单词
        """
        word_listbox.delete(0, tk.END)  # 清空列表框
        self.list_all_words(selected_book_name)

        # 添加单词到列表框
        idxes = list(self.cur_idx_words.keys())
        random.shuffle(idxes) if to_random else None
        [word_listbox.insert(tk.END, self.cur_idx_words[idx]) for idx in idxes]

        self.select_word(0, word_listbox)  # 选中第一个单词

    def select_word(self, word_idx: int, word_listbox: tk.Listbox):
        """触发选中左侧单词列表中的单词"""
        # 选中单词
        word_listbox.selection_clear(0, tk.END)
        word_listbox.selection_set(word_idx)
        word_listbox.activate(word_idx)
        word_listbox.event_generate("<<ListboxSelect>>")

        self.cur_word_obj = self.load_word_info(word_idx=word_idx)

    @staticmethod
    def parse_word_rule_1(line: str):
        """不为空行，不以#开头"""
        if line and len(line.strip()) > 0 and not line.strip().startswith("#"):
            return True
        return False

    def save_to_word_book(self, words: List[str], word_book_name: str):
        """将新增的文章的单词保存成单词书"""
        word_book_name = f'{word_book_name}-{str(datetime.now())[:10].replace("-", "")}'
        path = Path(self.book_dir_path) / word_book_name
        os.makedirs(path, exist_ok=True)
        with open(path / "naked-words.txt", "w", encoding="utf-8") as f:
            [f.write(word.lower() + "\n") for word in words]
        with open(path / "conf.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(
                {"name": word_book_name, "path": "naked-words.txt"},
                f,
                indent=4,
                allow_unicode=True,
            )

        for idx, word in enumerate(words):
            self.load_word_info(word.lower(), idx, word_book_name, True, True)
        print(f"finished {word_book_name}")

    @staticmethod
    def get_my_words(book_path: str, word_info_dir_path: str) -> List[MyWord]:  # noqa
        with open(book_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            words = [
                line.strip()
                for line in lines
                if not line.startswith("#") and len(line.strip()) > 0
            ]

        my_words: List[MyWord] = list()
        for word in words:
            word_info_path = f"{word_info_dir_path}/{word[0].lower()}/{word}.json"
            if not Path(word_info_path).exists():
                ic(word)
                continue
            try:
                my_word = MyWord.read_from_json(word_info_path)
                my_words.append(my_word)
            except Exception as e:
                ic(word)
                raise e
        return my_words

    @staticmethod
    def list_all_word_audio_paths(
        word_audio_libs_dir_path: Path,
        word_audio_path_dict: Dict[str, Dict[str, Dict[str, str]]] | None = None,
    ) -> Dict[str, Dict[str, Dict[str, str]]]:
        """加载所有单词音频的mp3/wav路径
        word_audio_path_dict[cook][us][oxford5000] = '../sources/word-audio-libs/oxford5000/us/c/cook.mp3'
        """

        def _f(
            path: Path,
            kind_name: str,
            source_name: str,
            result: Dict[str, Dict[str, Dict[str, str]]],
        ):
            for suffix in ["wav", "mp3"]:
                for audio_path in path.glob(f"*.{suffix}"):
                    word_name = audio_path.name.split(f".{suffix}")[0]
                    # result[cook][us][oxford5000] = '../sources/word-audio-libs/oxford5000/us/c/cook.mp3'
                    result[word_name][kind_name][source_name] = str(audio_path)

        word_audio_path_dict: Dict[str, Dict[str, Dict[str, str]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
            if word_audio_path_dict is None
            else word_audio_path_dict
        )

        # └───word-audio-libs             # word_audio_libs_dir_path
        #     └───oxford5000              # source_path
        #         ├───uk                  # kind_path
        #         │   └───c               # audio_dir
        #         │       └───cook.mp3
        #         └───us
        #             └───c
        #                 └───cook.mp3
        for source_path in word_audio_libs_dir_path.iterdir():
            kind_paths: List[Path] = [
                kind_path
                for kind_path in source_path.iterdir()
                if kind_path.name in list(AudioKind)  # uk | us | default | ai
            ]
            for kind_path in kind_paths:
                audio_dir_path_ls = [
                    audio_dir_path
                    for audio_dir_path in kind_path.iterdir()
                    if audio_dir_path.is_dir()
                    and audio_dir_path.name in list(string.ascii_lowercase)
                ]
                for audio_dir_path in audio_dir_path_ls:
                    _f(
                        audio_dir_path,
                        kind_path.name,
                        source_path.name,
                        word_audio_path_dict,
                    )
        return word_audio_path_dict

    @staticmethod
    def list_all_word_info_paths(
        word_info_libs_dir_path: Path, word_info_path_dict: Dict[str, Path]
    ) -> Dict[str, Path]:
        """加载所有单词信息的json路径"""
        word_info_path_dict: Dict[str, str | Path] = (
            dict() if word_info_path_dict is None else word_info_path_dict
        )
        for liter in list(string.ascii_lowercase):
            if not (word_info_libs_dir_path / liter).exists():
                continue
            for p in (word_info_libs_dir_path / liter).glob("*.json"):
                if not p.exists():
                    continue
                word_info_path_dict[p.name.replace(".json", "")] = p
        return word_info_path_dict


def test1():
    config = Config()
    book = Book(config=config)
    book.list_all_words("909")
    print(book.get_word_audio_path_with_download("cook"))


def create_909():
    """ """

    book = Book()
    book_names = book.list_all_book_names()
    if "909" not in book_names:
        print("Have no this book: 909")
        return

    book.list_all_words("909")

    for idx, word in book.cur_idx_words.items():
        print(idx, word)
        book.load_word_info_with_download(
            word, word_idx=idx, auto_fetch_word_info=True, auto_download_audio=True
        )


def create_oxford3000():
    book = Book()
    book_names = book.list_all_book_names()
    if "oxford3000" not in book_names:
        print("Have no this book: oxford3000")
        return

    book.list_all_words("oxford3000")

    for idx, word in book.cur_idx_words.items():
        book.load_word_info_with_download(
            word, word_idx=idx, auto_fetch_word_info=True, auto_download_audio=True
        )


def update_book(book_name: str):
    book = Book()
    book_names = book.list_all_book_names()
    if book_name not in book_names:
        print(f"Have no this book: {book_name}")
        return

    book.list_all_words(book_name)

    for idx, word in book.cur_idx_words.items():
        word_obj = book.load_word_info_with_download(
            word, word_idx=idx, auto_fetch_word_info=False, auto_download_audio=False
        )
        old_mp3 = word_obj.us_audio_path_dict.get("oxford5000")
        if not old_mp3 or not Path(old_mp3).exists():
            mp3 = book.word_audio_path_dict[word]["us"]["oxford5000"]
            if mp3 and Path(mp3).exists():
                word_obj.us_audio_path_dict["oxford5000"] = mp3
        old_mp3 = word_obj.uk_audio_path_dict.get("oxford5000")
        if not old_mp3 or not Path(old_mp3).exists():
            mp3 = book.word_audio_path_dict[word]["uk"]["oxford5000"]
            if mp3 and Path(mp3).exists():
                word_obj.uk_audio_path_dict["oxford5000"] = mp3

        word_obj.save_to_json(f"{book.word_info_libs_dir_path}/{word[0].lower()}")
        print(f"idx: {idx}, word: {word}")


if __name__ == "__main__":
    # create_909()
    update_book("oxford3000")
