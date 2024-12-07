import os
from multiprocessing import Pool
from pathlib import Path

from pydub import AudioSegment

from src.utils import get_my_words


def mp3_combine(name, s_idx, e_idx, my_words, abs_path):
    combined = AudioSegment.empty()

    for my_word in my_words[s_idx:e_idx]:
        us_mp3 = my_word.us_audio_path_dict.get("oxford5000")
        uk_mp3 = my_word.uk_audio_path_dict.get("oxford5000")

        if not us_mp3 or not os.path.exists(abs_path / us_mp3):
            print(my_word.word)
            continue
        combined += AudioSegment.from_file(abs_path / us_mp3)
        combined += AudioSegment.from_file(abs_path / uk_mp3)
        combined += AudioSegment.from_file(abs_path / us_mp3)
        combined += AudioSegment.from_file(abs_path / uk_mp3)
        combined += AudioSegment.from_file(abs_path / us_mp3)
        combined += AudioSegment.from_file(abs_path / uk_mp3)
        combined += AudioSegment.silent(duration=1000)

    combined.export(name, format="mp3")
    print(f"已合成{name}")


def gen_mp3(
    save_path,
    book_path: str,
    word_info_dir_path: str,
    per_num: int = 100,
):
    my_words = get_my_words(book_path, word_info_dir_path)
    save_dir_path = Path(save_path).parent
    os.makedirs(save_dir_path, exist_ok=True)
    save_name = Path(save_path).name
    abs_path = Path(__file__).parent.parent.absolute()
    idxes = sorted(list(set(list(range(0, len(my_words), per_num)) + [len(my_words)])))
    if (idxes[-1] - idxes[-2]) < per_num // 2:
        end = idxes.pop()
        idxes.pop()
        idxes.append(end)
    pool = Pool(20)
    for s_idx, e_idx in zip(idxes[:-1], idxes[1:]):
        name = (
            save_name.rsplit(".", maxsplit=1)[0]
            + f"-{e_idx}."
            + save_name.rsplit(".", maxsplit=1)[1]
        )
        pool.apply_async(mp3_combine, args=(name, s_idx, e_idx, my_words, abs_path))
    pool.close()
    pool.join()


if __name__ == "__main__":
    gen_mp3(
        "../test/mp3/oxford3000.mp3",
        "../sources/word-book/oxford3000/words-3000.txt",
        "../sources/word-info-libs",
    )
