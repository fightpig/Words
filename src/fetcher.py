import os
import time

import requests
from bs4 import BeautifulSoup
from icecream import ic

from src.utils import download_file


class Oxford:
    url: str = 'https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000'
    mp3_uri: str = 'https://www.oxfordlearnersdictionaries.com/'
    headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'  # noqa
    }

    @classmethod
    def fetch_5000_audio(cls, save_dir_path='oxford5000', override=False):
        def _f(p, kind):
            mp3_path = li.find('div', {'class': f'sound audio_play_button icon-audio pron-{kind}'})['data-src-mp3']
            os.makedirs(f'{p}/{kind}/{word[0].lower()}', exist_ok=True)
            save_path = f'{p}/{kind}/{word[0].lower()}/{word}.mp3'

            if override or not os.path.exists(save_path):
                re, *_ = download_file(save_path=save_path, url=cls.mp3_uri + mp3_path, headers=cls.headers)
                if re is False:
                    with open(f'{p}/{kind}-fail.txt', "a+") as f:
                        f.write(word + '\n')
                else:
                    ic(f'Finish {word} {kind.upper()} MP3')

        response = requests.get(cls.url, headers=cls.headers)
        li_list = (
            BeautifulSoup(response.text, 'html.parser')
            .find('div', {'id': 'informational-content'})
            .find('div', {'id': 'wordlistsContentPanel'})
            .find('ul', {'class': 'top-g'}).findAll('li')
        )
        ic(f'total {len(li_list)} words')
        time.sleep(3)

        words = list()
        for idx, li in enumerate(li_list, 1):
            word = li.a.text
            words.append(word)
            ic(f'--------------> {idx} {word}')
            _f(save_dir_path, 'us')
            _f(save_dir_path, 'uk')
            ic('')

        with open(f'{save_dir_path}/oxford5000.txt', 'w') as f:
            [f.write(word + '\n') for word in words]


def test_oxford_5000():
    Oxford.fetch_5000_audio('oxford5000', override=False)


if __name__ == '__main__':
    test_oxford_5000()
