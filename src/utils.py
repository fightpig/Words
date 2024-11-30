import json
import os
from pathlib import Path
from typing import Tuple

import requests
import yaml


def download_file(save_path: str | Path, url: str, headers: dict = None) -> Tuple[bool, int, Exception]:
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


def save_to_json_or_yaml(data: dict, save_path: str | Path, to_json: bool = True, to_print=False):
    save_path = Path(save_path) if isinstance(save_path, str) else save_path
    os.makedirs(save_path.parent, exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as file:
        if to_json:
            json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            yaml.safe_dump(data, file, indent=4, allow_unicode=True)
        print(f'Saved {save_path}') if to_print else None


def save_to_json(data: dict, save_path: str | Path, to_print=False):
    save_to_json_or_yaml(data, save_path, to_json=True, to_print=to_print)


def save_to_yaml(data: dict, save_path: str | Path, to_print=False):
    save_to_json_or_yaml(data, save_path, to_json=False, to_print=to_print)


def read_from_json_or_yaml(file_path: str | Path, from_json: bool = True) -> dict:  # noqa
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file) if from_json else yaml.safe_load(file)


def read_from_json(file_path: str | Path) -> dict:  # noqa
    return read_from_json_or_yaml(file_path, from_json=True)


def read_from_yaml(file_path: str | Path) -> dict:  # noqa
    return read_from_json_or_yaml(file_path, from_json=False)
