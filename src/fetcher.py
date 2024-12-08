import json
import os
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from icecream import ic

from src.book import MyWord
from src.utils import (
    download_file,
    save_to_json,
    HEADERS,
    my_logger,
    read_file,
    read_from_json,
)

load_dotenv("../conf/.env")


class Oxford:
    url: str = os.environ.get("oxford5000-url")
    mp3_uri: str = os.environ.get("oxford5000-mp3-uri")

    @classmethod
    def download_5000_word_and_audio(cls, save_dir_path="oxford5000", override=False):
        def _f(p, kind):
            mp3_path = li.find(
                "div", {"class": f"sound audio_play_button icon-audio pron-{kind}"}
            )["data-src-mp3"]
            os.makedirs(f"{p}/{kind}/{word[0].lower()}", exist_ok=True)
            save_path = f"{p}/{kind}/{word[0].lower()}/{word}.mp3"

            if override or not os.path.exists(save_path):

                re, *_ = download_file(
                    save_path=save_path,
                    url=cls.mp3_uri + "/" + mp3_path,
                    headers=HEADERS,
                )

                if re is False:
                    with open(f"{p}/{kind}-fail.txt", "a+") as f:
                        f.write(word + "\n")
                else:
                    ic(f"Finish {word} {kind.upper()} MP3")

        response = requests.get(cls.url, headers=HEADERS)
        li_list = (
            BeautifulSoup(response.text, "html.parser")
            .find("div", {"id": "informational-content"})
            .find("div", {"id": "wordlistsContentPanel"})
            .find("ul", {"class": "top-g"})
            .findAll("li")
        )
        ic(f"total {len(li_list)} words")
        time.sleep(3)

        words = list()
        for idx, li in enumerate(li_list, 1):
            word = li.a.text
            words.append(word)
            ic(f"--------------> {idx} {word}")
            _f(save_dir_path, "us")
            _f(save_dir_path, "uk")
            ic("")

        with open(f"{save_dir_path}/oxford5000.txt", "w") as f:
            [f.write(word + "\n") for word in words]


class Base:
    url: str = None
    headers: dict = HEADERS

    @classmethod
    def _request(cls, word) -> BeautifulSoup:
        url = cls.url.format(word=word)
        response = requests.get(url, headers=cls.headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @classmethod
    def fetch(cls, word, **kwargs) -> dict | MyWord | None:
        pass


class Sogou(Base):
    url: str = os.environ.get("sogou-url")

    @classmethod
    def fetch(
        cls, word, to_my_word=False, save_json_path=None, override=False
    ) -> dict | MyWord | None:
        try:
            if override is False and Path(save_json_path).exists():
                json_data = read_from_json(save_json_path)
                my_logger.info(f"{word}.json已存在")
            else:
                soup = cls._request(word)
                content = soup.findAll("script")[0].text
                content = content.replace("\\u002F", "/")
                content = content.split(";(function")[0]
                content = content.replace("window.__INITIAL_STATE__=", "")
                json_data = json.loads(content)
                save_to_json(json_data, save_json_path) if save_json_path else None
            return cls.to_my_word(word, json_data) if to_my_word else json_data
        except Exception as e:
            my_logger.exception(e)
            my_logger.error(f"Fail to fetch {word}")

    @staticmethod
    def to_my_word(word, word_json_data: dict) -> MyWord:
        word_obj = MyWord(word=word)

        for item in (
            word_json_data.get("textTranslate")
            .get("translateData")
            .get("wordCard")
            .get("usualDict")
        ):
            meaning = item.get("values")[0]
            pos = item.get("pos")
            word_obj.meaning_dict["sogou"][pos] = meaning

        for level in ["kaoyan", "CET6", "CET4", "gaokao", "zhongkao"]:
            pos_meanings = defaultdict(list)
            for sub_item in (
                word_json_data.get("textTranslate")
                .get("translateData")
                .get(level, dict())
                .get("exam_freq_info", list())
            ):
                pos = sub_item.get("pos")
                meaning = (
                    sub_item.get("chinese") + f'[出现{sub_item.get("sense_tier")}次)]'
                )
                pos_meanings[pos].append(meaning)

            if pos_meanings:
                for pos, meanings in pos_meanings.items():
                    word_obj.meaning_dict[f"sogou-{level}"][pos] = ";".join(meanings)

        for item in (
            word_json_data.get("textTranslate")
            .get("translateData")
            .get("voice")
            .get("phonetic")
        ):
            phonetic = item.get("text")
            audio_url = item.get("filename")

            if item.get("type") == "uk":
                word_obj.uk_phonetic = phonetic
                word_obj.uk_audio_url_dict["sogou"] = audio_url
            else:
                word_obj.us_phonetic = phonetic
                word_obj.us_audio_url_dict["sogou"] = audio_url

        book = word_json_data.get("textTranslate").get("translateData").get("book")
        if isinstance(book, dict):
            for idx, item in enumerate(book.get("yingyinNormal")):
                audio_url = item.get("audioUrl")
                en = item.get("en")
                zh = item.get("zh")
                word_obj.sentence_dict["sogou"][idx]["en"] = en
                word_obj.sentence_dict["sogou"][idx]["cn"] = zh
                word_obj.sentence_audio_url_dict["sogou"][idx] = audio_url

        return word_obj


class Bing(Base):
    url: str = os.environ.get("bing-url")
    headers: dict = {
        "authority": "cn.bing.com",
        "method": "GET",
        "scheme": "https",
        **HEADERS,
    }

    @staticmethod
    def parse_phonetic(content, uk: bool = True) -> str | None:
        try:
            div_class = "hd_pr" if uk else "hd_prUS"
            replace_word = "英" if uk else "美"
            return (
                content.find("div", {"class": div_class})
                .text.replace(" ", " ")
                .replace(replace_word, "")
                .strip()
            )
        except Exception:
            return None

    @classmethod
    def fetch(cls, word, sentence_num=3) -> MyWord | None:
        try:
            soup = cls._request(word)
            # 从word_div中提取相关内容
            word_div = soup.find("div", class_="lf_area")

            # 音标、发音、含义、图例
            word_def = word_div.find("div", {"class": "qdef"})  # noqa

            # 提取音标
            us_phonetic = cls.parse_phonetic(word_def, uk=False)
            uk_phonetic = cls.parse_phonetic(word_def, uk=True)

            # 提取发音链接
            us_audio_url = word_def.find("a", {"id": "bigaud_us"})[
                "data-mp3link"
            ]  # noqa
            uk_audio_url = word_def.find("a", {"id": "bigaud_uk"})[
                "data-mp3link"
            ]  # noqa

            # 含义
            try:
                speeches = word_def.find("ul").findAll("span", {"class", "pos"})
                definition = word_def.find("ul").findAll(
                    "span", {"class": "def b_regtxt"}
                )  # noqa
                meaning_dict = {
                    s.text if s.text.endswith(".") else s.text + ".": d.text
                    for s, d in zip(speeches, definition)
                }
            except Exception:
                meaning_dict = dict()

            # 提取例句
            sentence_dict = defaultdict(dict)
            sentence_audio_url_dict = dict()
            try:
                se_div = word_div.find("div", {"class": "se_div"}).find(
                    "div", {"id": "sentenceSeg"}
                )

                for idx, se in enumerate(se_div.findAll("div", {"class": "se_li1"}), 1):
                    en = "".join(
                        [
                            w.text
                            for w in se.find(
                                "div", {"class": "sen_en b_regtxt"}
                            ).find_all()
                        ]
                    )  # noqa
                    cn = "".join(
                        [
                            w.text
                            for w in se.find(
                                "div", {"class": "sen_cn b_regtxt"}
                            ).find_all()
                        ]
                    )  # noqa
                    mp3 = se.find("div", {"class": "mm_div"}).find("a")["data-mp3link"]
                    sentence_dict[idx] = dict(en=en, cn=cn)
                    sentence_audio_url_dict[idx] = mp3
                    if idx == sentence_num:
                        break
            except Exception:
                pass

            # 提取单词的示例图片链接
            try:
                pictures = word_div.find("div", {"class": "img_area"}).find_all("img")
                picture_url_ls = [image["src"] for image in pictures]
                picture_url_ls = [
                    f'{link.rsplit("&", maxsplit=2)[0]}' for link in picture_url_ls
                ]
            except AttributeError:
                picture_url_ls = list()

            meaning_str = ""
            meaning_ls = list()
            for k, v in meaning_dict.items():
                if not k.endswith("."):
                    k = k + "."  # '网络' -> '网络.'
                kv = k + " " + v + "\n"
                meaning_str += kv
                meaning_ls.append(kv)
            meaning_str = meaning_str[:-1]

            return MyWord(
                word=word,
                us_phonetic=us_phonetic,
                uk_phonetic=uk_phonetic,
                us_audio_url_dict=dict(bing=us_audio_url),
                uk_audio_url_dict=dict(bing=uk_audio_url),
                meaning_str=dict(bing=meaning_str),
                meaning_dict=dict(bing=meaning_dict),
                sentence_num=sentence_num,
                sentence_dict=dict(bing=sentence_dict),
                sentence_audio_url_dict=dict(bing=sentence_audio_url_dict),
                picture_num=len(picture_url_ls),
                picture_url_dict=dict(bing=picture_url_ls),
            )
        except Exception as e:
            my_logger.exception(e)


class Baidu:
    us_audio_url: str = os.environ.get("baidu-us-audio-url")
    uk_audio_url: str = os.environ.get("baidu-uk-audio-url")

    @classmethod
    def download_audio(
        cls, text: str, save_dir_path: str | Path, lan: str | None = None
    ) -> List[bool]:
        """
        :param text:
        :param lan: None | us | uk
        :param save_dir_path
        :return:
        """
        urls = {
            "us": cls.us_audio_url.format(text=text),
            "uk": cls.uk_audio_url.format(text=text),
        }

        if lan == "uk":
            urls.pop("us")
        if lan == "us":
            urls.pop("uk")

        res = list()
        for lan, url in urls.items():
            re, *_ = download_file(f"{save_dir_path}/{lan}-{text}.mp3", url, HEADERS)
            res.append(re)
        return res


def test_oxford_5000():
    Oxford.download_5000_word_and_audio("oxford5000", override=False)


def test_sogou():
    cn = 0

    # for line in read_file("../sources/word-book/oxford3000/words-3000.txt"):
    for line in read_file(
        "D:\Words\sources\word-audio-libs\oxford5000\words-5000-excluded-3000"
    ):
        if line.strip().startswith("#"):
            continue
        word = line.strip().split(" ")[0]
        if len(word) == 0:
            continue
        cn += 1
        my_word = Sogou.fetch(
            word,
            to_my_word=True,
            save_json_path=f"../sources/sogou-word-info-libs/{word[0]}/{word}.json",
        )
        ic(cn, my_word)


def test_bing():
    my_word = Bing.fetch("hero")
    ic(my_word)


def test_baidu():
    Baidu.download_audio("Need to word hard", "../test", lan=None)


if __name__ == "__main__":
    # test_oxford_5000()
    test_sogou()
    # test_bing()
    # test_baidu()

    ...
