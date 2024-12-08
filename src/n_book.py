import json
import os
import string
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import random
from pprint import pprint
from tkinter import messagebox
import tkinter as tk
from typing import List, Dict, Union, Tuple, Self

import yaml
from icecream import ic
from pydantic import BaseModel

from src.configuration import Config, AudioKind, AudioSource

from src.utils import (
    save_to_json,
    save_to_yaml,
    read_from_json,
    read_from_yaml,
    read_file,
    download_audio_file,
    my_logger,
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

    def get_word_meaning(self, word_info_priority: List[str]) -> Dict[str, str] | None:
        """根据配置文件的优先级，获取含义

        :param word_or_obj:
        :param word_info_priority:
            word-info-libs:
            - bing  # bing-网络.
            - nce
            - sogou
            - sogou-cet4
        """
        # priority: List[str] = [
        #     kind for kind in self.config["priority"]["word-info-libs"]
        # ]

        for source in word_info_priority:
            meaning_dict: Dict[str, str] = self.meaning_dict.get(source)
            if meaning_dict:
                return meaning_dict

            if len(source.split("-")) == 2:
                source, key = source.split("-")
                meaning_dict: Dict[str, str] = self.meaning_dict.get(source)
                if meaning_dict:
                    if key and key in meaning_dict:
                        return {key: meaning_dict.get(key)}
                    return meaning_dict

    @staticmethod
    def get_word_audio_path_with_download(
        my_word: "MyWord",
        word_audio_path_dict: Dict[str, Dict[str, str]],
        word_audio_priority: Dict[str, List[str]],
        word_audio_libs_dir_path,
        auto_download=True,
        using_baidu_when_fail=True,
        refetch_audio=False,
    ) -> List[str]:
        """根据配置文件的优先级，从本地word-audio-libs库中依次寻找对应的音频"""
        for kind in list(AudioKind):
            audio_path_dict = (
                word_audio_path_dict.get(kind) if word_audio_path_dict else dict()
            )
            (
                setattr(my_word, f"{kind}_audio_path_dict", audio_path_dict)
                if audio_path_dict
                else None
            )

        priority: List[Tuple[str, str]] = [
            (source, kind)
            # for source in self.config["priority"]["word-audio-libs"]["path"]
            # for kind in self.config["priority"]["word-audio-libs"]["path"].get(source)
            for source in word_audio_priority.keys()
            for kind in word_audio_priority[source]
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
                    refetch_audio=refetch_audio,
                    to_print=True,
                )
                audio_paths.append(audio_path) if ret else None
        return audio_paths

    @staticmethod
    def load_word_info_with_download(
        word: str,
        word_json_path: Path | None,
        word_info_libs_dir_path: Path,
        sogou_word_info_libs_dir_path: Path,
        word_audio_libs_dir_path,
        word_audio_path_dict: Dict[str, Dict[str, Dict[str, str]]],
        word_audio_priority: Dict[str, List[str]],
        auto_fetch_word_info: bool = False,
        auto_download_audio: bool = False,
        refetch_word=False,
        refetch_audio=False,
    ) -> "MyWord":
        """加载单词信息，不存在时从网上爬取，并更新"""
        from src.fetcher import Bing, Sogou

        my_word = MyWord(word=word)
        need_save = False

        if refetch_word or not word_json_path or not word_json_path.exists():
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
            # TODO 判断是否有bing和sogou信息，否则重新下载

        if need_save:  # 保存json
            my_word.save_to_json(word_info_libs_dir_path / f"{word[0].lower()}")
            my_logger.info(f"{my_word.word}.json已保存")

        MyWord.get_word_audio_path_with_download(
            my_word,
            word_audio_path_dict.get(my_word.word),
            word_audio_priority,
            word_audio_libs_dir_path,
            auto_download_audio,
            auto_download_audio,
            refetch_audio=refetch_audio,
        )
        return my_word

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
        to_my_word: "MyWord",
        from_my_word: Union["MyWord", None],
        exclude_attrs=("id", "word", "cur_book_name"),
    ) -> "MyWord":
        if from_my_word is None:
            return to_my_word

        updated_word = to_my_word.model_copy(deep=True)
        for attr, value in from_my_word:
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

    def list_all_book_names(self) -> List[str]:
        """单词书名列表"""
        try:
            for p in self.book_dir_path.iterdir():
                config = Config(p / "conf.yaml")
                self.bookname_dirs[str(config.get("name"))] = p.name
        except Exception as e:
            my_logger.exception(e)
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
            self.list_all_book_names() if not self.bookname_dirs else None
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
            my_logger.exception(e)
            # if self.showerror_by_messagebox:
            #     messagebox.showerror("错误", f"无法打开单词书: {book_name}\n{e}")
            raise Exception(f"无法打开单词书: {book_name}")
        else:
            self.cur_book_name = book_name
            self.cur_word_idxes = {word: idx for idx, word in enumerate(words)}
            self.cur_idx_words = {idx: word for idx, word in enumerate(words)}

    def get_word_info_priority(self) -> List[str]:
        """
        :return:
            - bing  # bing-网络.
            - nce
            - sogou
            - cet4
            - cet6
        """
        return self.config["priority"]["word-info-libs"]

    def get_word_audio_priority(self) -> Dict[str, List[str]]:
        """
        :return:
            oxford5000:
                - us
                - uk
            nce:
                - us
                - uk
        """
        return self.config["priority"]["word-audio-libs"]["path"]

    def get_my_word_with_download(
        self,
        word_or_idx: str | int,
        auto_fetch_word_info=True,
        auto_download_audio=True,
        refetch_word=False,
        refetch_audio=False,
    ) -> MyWord:
        word = (
            word_or_idx
            if isinstance(word_or_idx, str)
            else self.cur_idx_words.get(word_or_idx)
        )
        idx = self.cur_word_idxes.get(word)
        my_word = MyWord.load_word_info_with_download(
            word,
            word_json_path=self.word_info_path_dict.get(word),
            word_info_libs_dir_path=self.word_info_libs_dir_path,
            sogou_word_info_libs_dir_path=self.sogou_word_info_libs_dir_path,
            word_audio_libs_dir_path=self.word_audio_libs_dir_path,
            word_audio_path_dict=self.word_audio_path_dict,
            word_audio_priority=self.get_word_audio_priority(),
            auto_fetch_word_info=auto_fetch_word_info,
            auto_download_audio=auto_download_audio,
            refetch_word=refetch_word,
            refetch_audio=refetch_audio,
        )
        my_word.idx = idx
        my_word.cur_book_name = self.cur_book_name
        return my_word

    def get_my_word(
        self,
        word_or_idx: str | int,
    ) -> MyWord:
        return self.get_my_word_with_download(
            word_or_idx, auto_fetch_word_info=False, auto_download_audio=False
        )

    def get_word_meaning(self, my_word: MyWord) -> Dict[str, str]:
        return my_word.get_word_meaning(self.get_word_info_priority())

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
        with open(book_path, "r", encoding="utf-8") as f:  # TODO
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

    @staticmethod
    def parse_word_rule_1(line: str):
        """不为空行，不以#开头"""
        if line and len(line.strip()) > 0 and not line.strip().startswith("#"):
            return True
        return False

    @staticmethod
    def create_a_book(book_name: str):
        """根据单词下载单词信息和音频"""
        book = Book()
        book_names = book.list_all_book_names()
        if book_name not in book_names:
            my_logger.info(f"Have no this book: {book_name}")
            return

        book.list_all_words(book_name)
        for idx, word in book.cur_idx_words.items():
            my_word = book.get_my_word_with_download(
                word,
                auto_fetch_word_info=True,
                auto_download_audio=True,
                refetch_word=True,
                refetch_audio=False,
            )
            pprint(my_word.get_word_meaning(book.get_word_info_priority()))


if __name__ == "__main__":
    Book.create_a_book("oxford3000")
