import json
import os
import string
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import random
from tkinter import messagebox
import tkinter as tk
from typing import List, Dict, Union, Tuple

import yaml
from pydantic import BaseModel

from src.configuration import Config, AudioKind
from src.utils import save_to_json, save_to_yaml, read_from_json, read_from_yaml


class MyWord(BaseModel):
    word: str
    """单词"""
    id: int | str | None = None
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
        self.cur_word_info_str = ""
        self.cur_audio_path = None

        # [(nce, us), (nce, uk), (oxford5000, us), (oxford5000, uk)]
        self.priority: List[Tuple[str, str]] = list()
        self.word_audio_path_dict: Dict[str, Dict[str, Dict[str, str]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(str))
        )
        self.word_info_path_dict: Dict[str, str | Path] = dict()
        self.load_audio_libs()
        self.load_info_libs()

    def load_audio_libs(self):
        """加载所有单词音频的mp3/wav路径"""

        def _f(
            path: Path,
            kind_name: str,
            source_name: str,
            result: Dict[str, Dict[str, Dict[str, str]]],
        ):
            for suffix in ["wav", "mp3"]:
                for audio_path in path.glob(f"*.{suffix}"):
                    word_name = audio_path.name.split(f".{suffix}")[0]
                    result[word_name][kind_name][source_name] = str(audio_path)

        for source_path in self.word_audio_libs_dir_path.iterdir():
            kind_names: List[Path] = [
                kind_name
                for kind_name in source_path.iterdir()
                if kind_name.name in list(AudioKind)
            ]
            for kind_path in kind_names:
                audio_dir_ls = [
                    audio_dir_path
                    for audio_dir_path in kind_path.iterdir()
                    if audio_dir_path.is_dir()
                    and audio_dir_path.name in list(string.ascii_lowercase)
                ]
                if len(audio_dir_ls) > 0:
                    for audio_dir in audio_dir_ls:
                        _f(
                            audio_dir,
                            kind_path.name,
                            source_path.name,
                            self.word_audio_path_dict,
                        )
                else:
                    _f(
                        kind_path,
                        kind_path.name,
                        source_path.name,
                        self.word_audio_path_dict,
                    )

    def load_info_libs(self):
        """加载所有单词信息的json路径"""
        for liter in list(string.ascii_lowercase):
            if not (self.word_info_libs_dir_path / liter).exists():
                continue
            for p in (self.word_info_libs_dir_path / liter).glob("*.json"):
                if not p.exists():
                    continue
                self.word_info_path_dict[p.name.replace(".json", "")] = p

    def list_book_names(self) -> List[str]:
        """单词书名列表"""
        try:
            for p in self.book_dir_path.iterdir():
                config = Config(p / "conf.yaml")
                self.bookname_dirs[str(config.get("name"))] = p.name
        except Exception as e:
            print(e)
            (
                messagebox.showerror("错误", "列出单词书出错")
                if self.showerror_by_messagebox
                else None
            )
        return list(self.bookname_dirs.keys())

    def list_words(self, book_name: str):
        """指定单词书的单词列表"""
        try:
            self.list_book_names() if not self.bookname_dirs else None
            book_dir = self.bookname_dirs.get(book_name)
            with open(
                self.book_dir_path / book_dir / "conf.yaml", "r", encoding="utf-8"
            ) as f:
                config = yaml.safe_load(f)
                self.config.update(**config)
            with open(
                f'{self.book_dir_path}/{book_dir}/{self.config.get("path")}',
                "r",
                encoding="utf-8",
            ) as f:
                lines = f.readlines()
            words = [line.strip() for line in lines if self.parse_word_rule_1(line)]
        except Exception as e:
            print(e)
            if self.showerror_by_messagebox:
                messagebox.showerror("错误", f"无法打开单词书: {book_name}\n{e}")
        else:
            self.cur_book_name = book_name
            self.cur_word_idxes = {word: idx for idx, word in enumerate(words)}
            self.cur_idx_words = {idx: word for idx, word in enumerate(words)}

    def load_word_info(
        self,
        word: str | None = None,
        word_idx: int | None = None,
        cur_book_name: str | None = None,
    ) -> MyWord:
        """加载单词信息"""
        return self.load_or_download_word_info(
            word,
            word_idx,
            cur_book_name,
            auto_fetch_word_info=False,
            auto_download_audio=False,
        )

    def load_or_download_word_info(
        self,
        word: str | None = None,
        word_idx: int | None = None,
        cur_book_name: str | None = None,
        auto_fetch_word_info: bool = False,
        auto_download_audio: bool = False,
    ) -> MyWord:
        """加载单词信息，不存在时从网上爬取创建"""
        assert word or word_idx is not None
        word = word if word else self.cur_idx_words.get(word_idx)
        word_idx = word_idx if word_idx else self.cur_word_idxes.get(word)
        cur_book_name = cur_book_name if cur_book_name else self.cur_book_name
        word_obj = MyWord(word=word, cur_book_name=str(cur_book_name), id=word_idx)
        word_json_path = self.word_info_path_dict.get(word)
        need_save = False

        if not word_json_path or not word_json_path.exists():
            need_save = True
            if auto_fetch_word_info:
                bing_word_obj, _ = self.fetch_new_word_info(word, using_fetcher="bing")
                sogou_word_obj, content = self.fetch_new_word_info(
                    word, using_fetcher="sogou"
                )
                word_obj = MyWord.update_my_word(word_obj, bing_word_obj)
                word_obj = MyWord.update_my_word(word_obj, sogou_word_obj)
                if content:
                    with open(
                            self.sogou_word_info_libs_dir_path / f"{word}.json",
                        "w",
                        encoding="utf-8",
                    ) as f:
                        json.dump(content, f, ensure_ascii=False, indent=4)
        else:
            with open(word_json_path, "r", encoding="utf-8") as f:
                kvs = json.load(f)
                kvs.pop("id", None)
                kvs.pop("cur_book_name", None)
                word_obj.__dict__.update(**kvs)

        if need_save:
            self.load_all_audio_paths(word_obj)
            word_obj.save_to_json(self.word_info_libs_dir_path / f"{word[0].lower()}")

        # 下载音频
        word_audio_path = self.get_word_audio_path(word_obj)
        if not word_audio_path and auto_download_audio:
            for source, url in word_obj.us_audio_url_dict.items():
                download_audio_file(
                    self.word_audio_libs_dir_path,
                    source,
                    "us",
                    word,
                    url,
                    using_baidu_when_fail=True,
                )
            for source, url in word_obj.uk_audio_url_dict.items():
                download_audio_file(
                    self.word_audio_libs_dir_path,
                    source,
                    "uk",
                    word,
                    url,
                    using_baidu_when_fail=True,
                )

        meaning_dict = self.get_word_meaning(word_obj)
        if not meaning_dict:
            print(word, "no meaning")

        return word_obj

    def _get_word_obj(self, word_or_obj: str | MyWord) -> MyWord:
        return (
            word_or_obj
            if isinstance(word_or_obj, MyWord)
            else self.load_word_info(word_or_obj)
        )

    def get_word_audio_path(self, word_or_obj: str | MyWord) -> Union[str, None]:
        """根据配置文件的优先级，从本地word-audio-libs库中依次寻找对应的音频"""
        word_obj = self._get_word_obj(word_or_obj)
        if word_obj is None:
            return None

        priority: List[Tuple[str, str]] = [
            (source, kind)
            for source in self.config["priority"]["word-audio-libs"]["path"]
            for kind in self.config["priority"]["word-audio-libs"]["path"].get(source)
        ]

        audio_path_dicts = {
            AudioKind.DEFAULT: word_obj.default_audio_path_dict or dict(),
            AudioKind.US: word_obj.us_audio_path_dict or dict(),
            AudioKind.UK: word_obj.uk_audio_path_dict or dict(),
            AudioKind.AI: word_obj.ai_audio_path_dict or dict(),
        }
        # TODO，没有mp3
        for source, kind in priority:
            audio_path = audio_path_dicts.get(kind).get(source)  # noqa
            if audio_path and Path(audio_path).exists():
                print(audio_path)
                return audio_path

    def get_word_meaning(self, word_or_obj: str | MyWord) -> Dict[str, str] | None:
        """根据配置文件的优先级，获取含义"""
        word_obj = self._get_word_obj(word_or_obj)
        if word_obj is None:
            return None

        priority: List[str] = [
            kind for kind in self.config["priority"]["word-info-libs"]
        ]

        for kind in priority:
            meaning_dict: Dict[str, str] = word_obj.meaning_dict.get(kind)
            if meaning_dict:
                if kind == "bing" and meaning_dict.get("网络."):
                    return {"网络.": meaning_dict.get("网络.")}  # TODO
                return meaning_dict

    @staticmethod
    def fetch_new_word_info(
        word, using_fetcher: str = "bing"
    ) -> Tuple[MyWord | None, dict | None]:
        """从网上爬取，创建一个新单词的json"""
        from fetcher import fetch_word_info_from_bing, fetch_word_info_from_sogou

        fetch_func = (
            fetch_word_info_from_bing
            if using_fetcher == "bing"
            else fetch_word_info_from_sogou
        )

        word_obj, content = None, None
        try:
            word_obj, content = fetch_func(word)
        except Exception as e:
            print(e)
            print(f"==> Fail to fetch word: {word} ")
        return word_obj, content

    def load_all_audio_paths(
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
                    getattr(word_obj, f"{kind_}_audio_path_dict").update(
                        {source: audio_path}
                    )
                    cn += 1

        word = word_or_obj.word if isinstance(word_or_obj, MyWord) else word_or_obj
        word_obj = word_or_obj if isinstance(word_or_obj, MyWord) else MyWord(word=word)
        cn = 0

        for kind in list(AudioKind):
            _f(kind)

        print(f"word: {word} have no audio") if cn == 0 else None
        return cn, word_obj

    def generate_word_listbox(
        self, selected_book_name: str, word_listbox: tk.Listbox, to_random=False
    ):
        """
        1 清空单词列表框
        2 获取单词书的所有单词插入到列表中
        3 选中第一个单词
        """
        word_listbox.delete(0, tk.END)  # 清空列表框
        self.list_words(selected_book_name)

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


def test1():
    config = Config()
    book = Book(config=config)
    book.list_words("909")
    print(book.get_word_audio_path("cook"))


def create_909():
    """ """

    book = Book()
    book_names = book.list_book_names()
    if "909" not in book_names:
        print("Have no this book: 909")
        return

    book.list_words("909")

    for idx, word in book.cur_idx_words.items():
        print(idx, word)
        book.load_or_download_word_info(
            word, word_idx=idx, auto_fetch_word_info=True, auto_download_audio=True
        )


def create_oxford3000():
    book = Book()
    book_names = book.list_book_names()
    if "oxford3000" not in book_names:
        print("Have no this book: oxford3000")
        return

    book.list_words("oxford3000")

    for idx, word in book.cur_idx_words.items():
        book.load_or_download_word_info(
            word, word_idx=idx, auto_fetch_word_info=True, auto_download_audio=True
        )


def update_book(book_name: str):
    book = Book()
    book_names = book.list_book_names()
    if book_name not in book_names:
        print(f"Have no this book: {book_name}")
        return

    book.list_words(book_name)

    for idx, word in book.cur_idx_words.items():
        word_obj = book.load_or_download_word_info(
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
