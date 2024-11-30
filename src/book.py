import os
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Union

from pydantic import BaseModel

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
    sentence_dict: Dict[str, Dict[int, Dict[str, str]]] | None = defaultdict(
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
    sentence_audio_url_dict: Dict[str, Dict[int, str]] | None = defaultdict(dict)
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
    sentence_audio_path_dict: Dict[str, Dict[int, str]] | None = defaultdict(dict)
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
        save_to_json(data=self.model_dump(), save_path=f'{save_dir_path}/{self.word}.json', to_print=to_print)

    def save_to_yaml(self, save_dir_path: str | Path, to_print=False):
        save_to_yaml(data=self.model_dump(), save_path=f'{save_dir_path}/{self.word}.yaml', to_print=to_print)

    @staticmethod
    def read_from_json(json_path: str | Path) -> 'MyWord':
        return MyWord(**read_from_json(json_path))

    @staticmethod
    def read_from_yaml(yaml_path: str | Path) -> 'MyWord':
        return MyWord(**read_from_yaml(yaml_path))

    def to_txt(self, save_dir_path: Union[str, Path]) -> None:
        os.makedirs(save_dir_path, exist_ok=True)
        with open(f'{save_dir_path}/{self.word}.txt', 'w', encoding='utf-8') as file:
            for attr_name in self.model_fields.keys():
                attr_value = getattr(self, attr_name)
                if attr_value is None:
                    attr_value = '__none__'
                elif isinstance(attr_value, (dict, list)):
                    attr_value = str(attr_value)
                elif isinstance(attr_value, Path):
                    attr_value = str(attr_value)
                file.write(f"# {attr_name}\n{attr_value}\n\n")

    @staticmethod
    def update_my_word(to_word_obj: 'MyWord',
                       from_word_obj: Union['MyWord', None],
                       exclude_attrs=('id', 'word', 'cur_book_name')
                       ) -> 'MyWord':
        if from_word_obj is None:
            return to_word_obj

        updated_word = to_word_obj.model_copy(deep=True)
        for attr, value in from_word_obj:
            if attr not in exclude_attrs and value is not None:
                current_value = getattr(updated_word, attr)
                if isinstance(value, defaultdict) and isinstance(current_value, defaultdict):
                    for k, v in value.items():
                        current_value[k] = v
                elif isinstance(value, dict) and isinstance(current_value, dict):
                    current_value.update(value)
                elif isinstance(value, list) and isinstance(current_value, list):
                    current_value.extend(value)
                else:
                    setattr(updated_word, attr, value)

        return updated_word
