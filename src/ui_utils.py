import tkinter as tk
from tkinter import ttk
from typing import Tuple

from utils import set_entry_value


def create_btn():
    pass


def create_label_with_entry_by_grid(
        parent_widget: tk.Widget,

        l_text: str,
        lg_row: int,
        lg_column: int,
        lg_padx: int,  # noqa
        lg_pady: int,  # noqa
        lg_sticky: str,

        eg_row: int,
        eg_column: int,
        eg_padx: int,  # noqa
        eg_pady: int,  # noqa
        eg_sticky: str,
        e_default_value: str | None = None,

        lg_kwargs: dict = dict(),  # noqa
        eg_kwargs: dict = dict(),  # noqa

) -> Tuple[tk.Label, tk.Entry]:
    """
    创建标签和输入框
    """
    label = ttk.Label(parent_widget, text=l_text)
    lg_kwargs.update(
        row=lg_row,
        column=lg_column,
        padx=lg_padx,
        pady=lg_pady,
        sticky=lg_sticky
    )
    label.grid(**lg_kwargs)

    entry = ttk.Entry(parent_widget, width=5)
    eg_kwargs.update(
        row=eg_row,
        column=eg_column,
        padx=eg_padx,
        pady=eg_pady,
        sticky=eg_sticky
    )
    entry.grid(**eg_kwargs)
    set_entry_value(entry, e_default_value) if e_default_value else None  # 设置默认值
    return label, entry
