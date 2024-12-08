import tkinter as tk
from typing import Dict, Union, Tuple, List

from book import Book
from configuration import Params
from media import Audio
from utils import RecorderHelper


def check_name(cls):
    if cls.name in cls.wrapper_names:
        raise ValueError(f"The name: {cls.name} is already used")
    cls.wrapper_names.append(cls.name)
    return cls


@check_name
class BaseWrapper:
    name = "base_wrapper"
    wrapper_names: List[str] = list()

    def __init__(self, parent: Union["BaseWrapper", None] = None, **kwargs):

        self.parent = parent
        self.kwargs = kwargs

        self.wrapper_dict: Dict[str, "BaseWrapper"] = (
            self.parent.wrapper_dict if parent else dict()  # noqa
        )
        self.widget: Union[tk.Tk, tk.Widget, None] = None
        self.sub_widgets: Dict[str, : Union[tk.Tk, tk.Widget]] = dict()
        self.wrapper_names: List[str] = list()

        self._book: Book | None = None
        self._audio: Audio | None = None
        self._params: Params | None = None
        self._recorder_helper: RecorderHelper | None = None

        self._init()
        self.create() if self.widget is None else None
        self.bind()

    def _init(self):
        self.wrapper_dict[self.name] = self
        self._set_value("book")
        self._set_value("audio")
        self._set_value("params")
        self._set_value("recorder_helper")

    def create(self):
        pass

    def bind(self):
        pass

    def _set_value(self, name):
        value = self.kwargs.get(name, None)
        value = (
            value
            if value
            else (None if self.parent is None else getattr(self.parent, name))
        )
        setattr(self, name, value)

    def get_wrapper(self, name: str | None = None):
        return self.wrapper_dict[self.name] if not name else self.wrapper_dict[name]

    def get_root_wrapper(self):
        return self.wrapper_dict["root_wrapper"]

    def get_word_content_frame_wrapper(self):
        return self.wrapper_dict["word_content_frame_wrapper"]

    def get_word_operation_frame_wrapper(self):
        return self.wrapper_dict["word_operation_frame_wrapper"]

    def get_sub_wrappers(self) -> Dict[str, "BaseWrapper"]:
        """获取所有子对象"""
        return {
            name: obj
            for name, obj in self.wrapper_dict.items()
            if obj.parent and obj.parent.name == self.name
        }

    def get_widget_size(self, widget: tk.Widget) -> Tuple[int, int]:
        self.get_wrapper("root_wrapper").widget.update()
        return widget.winfo_width(), widget.winfo_height()

    def get_all_heir_wrappers(self) -> Dict[str, "BaseWrapper"]:
        """获取所有子孙对象"""

        def _search(parent_name: str):
            sub_res: Dict[str, "BaseWrapper"] = dict()
            for name, obj in self.wrapper_dict.items():
                if obj.parent and obj.parent.name == parent_name:  # noqa
                    sub_res[name] = obj
            return sub_res

        def _f(parent_name: str | None = None):
            parent_name = self.name if not parent_name else parent_name
            sub_res = _search(parent_name)
            all_heir_objs.update(sub_res)
            for name in sub_res.keys():
                _f(name)

        all_heir_objs: Dict[str, "BaseWrapper"] = dict()
        _f()
        return all_heir_objs

    def get_sub_widget(self, name: str) -> tk.Tk | tk.Widget:
        """获取widget"""
        return self.sub_widgets[name]

    def destroy_all_widgets(self):
        widgets = [widget for widget in self.sub_widgets.values()]
        widgets.extend([obj.widget for obj in self.get_all_heir_wrappers().values()])

        for widget in widgets:
            for sub_widget in widget.winfo_children():
                sub_widget.destroy()

    def destroy_current_widget(self):
        widgets = [widget for widget in self.sub_widgets.values()]
        widgets.append(self.widget)

        for widget in widgets:
            for sub_widget in widget.winfo_children():
                sub_widget.destroy()

    def destroy_widget(self):
        if self.widget:
            for sub_widget in self.widget.winfo_children():
                sub_widget.destroy()
            self.widget.destroy()
            self.widget = None

    @property
    def book(self) -> Book:
        return self._book

    @book.setter
    def book(self, book: Book):
        self._book = book

    @property
    def audio(self) -> Audio:
        return self._audio

    @audio.setter
    def audio(self, audio: Audio):
        self._audio = audio

    @property
    def params(self) -> Params:
        return self._params

    @params.setter
    def params(self, params: Params):
        self._params = params

    @property
    def recorder_helper(self) -> RecorderHelper:
        return self._recorder_helper

    @recorder_helper.setter
    def recorder_helper(self, recorder_helper: RecorderHelper):
        self._recorder_helper = recorder_helper
