import json
import os
from pathlib import Path
from typing import List, Tuple

import requests
import yaml
from icecream import ic


def download_file(
    save_path: str | Path, url: str, headers: dict = None
) -> Tuple[bool, int, Exception]:
    ex = None
    re = False
    status_code = 200

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            os.makedirs(Path(save_path).parent, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)
            re = True
    except Exception as e:
        ex = e

    return re, status_code, ex


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


def get_my_words(book_path: str, word_info_dir_path: str) -> List["MyWord"]:  # noqa
    from src.book import MyWord

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
