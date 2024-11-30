import os
from pathlib import Path
from typing import Tuple

import requests


def download_file(save_path: str | Path, url: str, headers: dict=None) -> Tuple[bool, int, Exception]:
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

