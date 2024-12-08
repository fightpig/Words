from enum import StrEnum

import yaml


class AudioSource(StrEnum):
    """单词音频来源"""

    NCE = "nce"
    OXFORD5000 = "oxford5000"
    BING = "bing"
    SOGOU = "sogou"
    BAIDU = "baidu"


class AudioKind(StrEnum):
    """单词音频类型"""

    US = "us"
    UK = "uk"
    DEFAULT = "default"
    AI = "ai"


class Config(dict):
    def __init__(self, config_path="../conf/conf.yaml"):
        super().__init__()
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.update(self.config)


class Params(dict):
    def __init__(
        self,
        selected_word_idx: int = 0,
        episode_option_name="每集单词数",
        episode_option_value="300",
        play_interval=2,
        loop_cn=5,
        loop_interval=1,
        **kwargs: dict,
    ):
        super(Params, self).__init__(**kwargs)

        # 设置属性并添加到字典中
        self["episode_option_name"] = episode_option_name
        self["episode_option_value"] = int(episode_option_value)
        self["selected_word_idx"] = selected_word_idx
        self["play_interval"] = int(play_interval)
        self["loop_cn"] = int(loop_cn)
        self["loop_interval"] = int(loop_interval)

    def __setitem__(self, key, value):
        super(Params, self).__setitem__(key, value)
        # 更新实例的__dict__，使属性可以通过点操作符访问
        self.__dict__.update(self)

    def update(self, *args, **kwargs):
        super(Params, self).update(*args, **kwargs)
        # 更新实例的__dict__，使属性可以通过点操作符访问
        self.__dict__.update(self)

    def get_loop_cn(self) -> int:
        return int(self["loop_cn"])

    def get_loop_interval(self) -> int:
        return int(self["loop_interval"])

    def episode_option_name(self) -> int:
        return int(self["episode_option_name"])

    def get_episode_option_value(self) -> int:
        return int(self["episode_option_value"])

    def get_play_interval(self) -> int:
        return int(self["play_interval"])

    def get_selected_word_idx(self) -> int:
        return self["selected_word_idx"]


if __name__ == "__main__":
    # config = Config()
    # priority = [
    #     (source, kind)
    #     for source in config['word-audio-libs']['path']
    #     for kind in config['word-audio-libs']['path'].get(source)
    # ]
    # print(priority)

    # p['loop_interval'] = 10
    # print(p.loop_interval)
    # print(p['loop_interval'])

    # p.update(**{'loop_interval': 100})
    # print(p['loop_interval'])
    # print(p.loop_interval)
    ...
