from typing import List, Tuple

from book import MyWord, Book
from utils import get_mp3_duration


class RecordPlan:
    """分集录制计划，按时长或单词数"""

    def __init__(self,
                 book: Book,
                 s_word_idx: int,
                 e_word_idx: int,
                 episode_option_name: str,
                 episode_option_value: int,
                 loop: int,
                 ):
        self.book = book
        self.s_word_idx = s_word_idx
        self.e_word_idx = e_word_idx
        self.episode_option_name = episode_option_name
        self.episode_option_value = episode_option_value
        self.loop = loop

    def plan(self) -> List[Tuple[MyWord, MyWord, int, int]]:
        duration = 0
        cn = 0
        plans = list()
        s_word_obj = None
        for idx, (word_idx, word) in enumerate(self.book.cur_idx_words.items()):
            if int(self.s_word_idx) <= word_idx <= int(self.e_word_idx):
                word_obj = self.book.load_word_info(word)
                word_obj.id = word_idx
                audio_path = self.book.get_word_audio_path(word_obj)
                if not audio_path:
                    continue

                s_word_obj = word_obj if duration == 0 else s_word_obj
                duration += get_mp3_duration(audio_path) * self.loop
                cn += 1

                if self.episode_option_name == '每集分钟数':
                    if duration >= int(self.episode_option_value) * 60:
                        plans.append((s_word_obj, word_obj, duration, cn))
                        duration = 0
                        cn = 0
                    else:
                        if idx + 1 == len(self.book.cur_idx_words):
                            plans.append((s_word_obj, word_obj, duration, cn))
                            duration = 0
                            cn = 0
                else:
                    if cn >= int(self.episode_option_value):
                        plans.append((s_word_obj, word_obj, duration, cn))
                        duration = 0
                        cn = 0
                    else:
                        if idx + 1 == len(self.book.cur_idx_words):
                            plans.append((s_word_obj, word_obj, duration, cn))
                            duration = 0
                            cn = 0
        return plans
