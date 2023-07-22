from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget


class RaProgressBar(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setLayout(QHBoxLayout())

        self.__text_label1 = QLabel()
        self.__progress_bar = QProgressBar()
        self.__text_label2 = QLabel()

        self.layout().addWidget(self.__text_label1)
        self.layout().addWidget(self.__progress_bar)
        self.layout().addWidget(self.__text_label2)

    def update(self, value: int, maximum: int, text1: str, text2: str):
        self.__progress_bar.setValue(value)
        self.__progress_bar.setMaximum(maximum)
        self.__text_label1.setText(text1)
        self.__text_label2.setText(text2)
        self.show()

    def reset(self):
        self.__progress_bar.reset()
        self.__text_label1.setText("")
        self.__text_label2.setText("")
        self.hide()
