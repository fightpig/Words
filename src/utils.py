import json
import logging.config
import os
from pathlib import Path
from typing import List, Tuple, Any

import requests
import yaml

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
