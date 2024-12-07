import contextlib
from typing import List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from src.book import MyWord
from src.utils import get_my_words

# 注册新的字体（确保字体文件在您的文件系统中可用）
pdfmetrics.registerFont(TTFont("ArialUnicodeMS", "../sources/Arial Unicode MS.ttf"))


class PDF:
    def __init__(self, filename: str) -> None:
        # 创建 PDF 文档
        self.canvas = canvas.Canvas(filename, pagesize=letter)
        self.width, self.height = letter  # 获取页面宽度和高度
        self.left_x = 50
        self.y = self.height - 50
        self.column_width = self.width // 3 + 50
        self.line_height = 17  # 行高

    @contextlib.contextmanager
    def set_font(self, font_size: int) -> None:
        # 设置字体为 Arial Unicode MS
        self.canvas.setFont("ArialUnicodeMS", font_size)
        yield

    def wrap_text(
        self, text: str | List[str], font, font_size: int, length
    ) -> List[str]:
        lines = list()
        words = text.split() if isinstance(text, str) else text
        line = ""
        for word in words:
            if self.canvas.stringWidth(line + " " + word, font, font_size) < length:
                line += " " + word
            else:
                lines.append(line.strip())
                line = word
        lines.append(line.strip())
        return lines

    def write_line(
        self,
        x,
        y,
        word_phonetic: List[str],
        meaning: str,
        wp_color: colors,
        meaning_color: colors,
        font_size: int,
    ) -> Tuple[int, int]:
        with self.set_font(font_size):
            # 写单词和音标，1列

            # 写中文含义，1列
            lines = self.wrap_text(
                word_phonetic, "ArialUnicodeMS", font_size, self.column_width - 50
            )
            old_y = y
            for idx, line in enumerate(lines):
                self.canvas.setFillColor(wp_color)
                if idx == 0:
                    self.canvas.drawString(x, old_y, line)
                else:
                    self.canvas.drawString(x + 50, old_y, line)
                old_y -= self.line_height

            # 写中文含义，1列
            lines = self.wrap_text(
                meaning,
                "ArialUnicodeMS",
                font_size,
                (self.width - self.column_width - 50),
            )
            for idx, line in enumerate(lines):
                self.canvas.setFillColor(meaning_color)
                if idx == 0:
                    self.canvas.drawString(x + self.column_width, y, line)
                else:
                    self.canvas.drawString(x + self.column_width + 10, y, line)
                y -= self.line_height
            y = min(old_y, y)
        return x, y

    def write(self, my_words: List[MyWord], font_size: int) -> None:
        x = self.left_x
        y = self.y
        cn = 0
        for idx, my_word in enumerate(my_words):
            if (cn + 1) % 21 == 0:
                self.canvas.setFillColor(colors.red)
                self.canvas.drawString(0, y, "-" * int(self.width - 100))
                y -= self.line_height

            word_phonetic = [
                f"{idx + 1}. {my_word.word}",
                f"美[{my_word.us_phonetic}]",
                f"英[{my_word.uk_phonetic}]",
            ]
            net_meaning = my_word.meaning_dict.get(
                "bing", my_word.meaning_dict.get("Bing", dict())
            ).get("网络.")
            meaning = (
                net_meaning
                if net_meaning
                else " ".join(
                    [
                        f"{k} {v}"
                        for k, v in my_word.meaning_dict.get(
                            "bing", my_word.meaning_dict.get("Bing", dict())
                        ).items()
                    ]
                )
            )
            x, y = self.write_line(
                x, y, word_phonetic, meaning, colors.blue, colors.green, font_size
            )

            if y < 72:
                y = self.y
                self.canvas.showPage()

            cn += 1

        self.canvas.save()


def gen_pdf(
    pdf_filename: str, book_path: str, word_info_dir_path: str, font_size: int
) -> None:
    my_words = get_my_words(book_path, word_info_dir_path)
    pdf = PDF(pdf_filename)
    pdf.write(my_words, font_size)

    for idx, my_word in enumerate(my_words, 1):
        if idx % 100 == 1 or idx % 100 == 0:
            print(idx, my_word.word)


if __name__ == "__main__":
    gen_pdf(
        "oxford3000.pdf",
        "../sources/word-book/oxford3000/words-3000.txt",
        "../sources/word-info-libs",
        font_size=10,
    )
