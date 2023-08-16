from typing import Any, Callable

from PySide6.QtCore import QThread


class RaQThreadWorker(QThread):
    def __init__(self, f: Callable[[], Any], *args, **kwargs):
        super().__init__()
        self.__f = f
        self.__args = args
        self.__kwargs = kwargs

    def run(self):
        self.__ret = self.__f(*self.__args, **self.__kwargs)

    @property
    def result(self):
        return self.__ret
