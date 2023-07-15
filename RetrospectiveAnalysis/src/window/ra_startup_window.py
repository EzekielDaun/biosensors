import logging

from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .ra_active_converter_dialog import RaActiveConverterDialog
from .ra_passive_analyzer_window import RaPassiveAnalyzerWindow
from .ra_quick_analyzer_window import RaQuickAnalyzerWindow
from .ra_watcher_window import RaWatcherWindow

logger = logging.getLogger(__name__)


class RaStartupWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__central_widget = self.RaStartupWindowCentralWidget()
        self.setCentralWidget(self.__central_widget)

        self.__central_widget.passive_button.clicked.connect(self.slot_passive_analyzer)
        self.__central_widget.active_button.clicked.connect(self.slot_active_converter)
        self.__central_widget.watch_mode_button.clicked.connect(self.slot_watch_mode)
        self.__central_widget.quick_analyzer_button.clicked.connect(
            self.slot_quick_analyzer
        )

    def slot_passive_analyzer(self):
        passive_analyzer_window = RaPassiveAnalyzerWindow()
        passive_analyzer_window.signal_close.connect(self.show)
        self.hide()
        passive_analyzer_window.show()

    def slot_active_converter(self):
        dir = QFileDialog.getExistingDirectory()
        if dir:
            active_converter_dialog = RaActiveConverterDialog(dir, self)
            active_converter_dialog.accepted.connect(self.show)
            active_converter_dialog.rejected.connect(self.show)
            self.hide()
            active_converter_dialog.show()

    def slot_watch_mode(self):
        watcher_window = RaWatcherWindow()
        watcher_window.signal_close.connect(self.show)
        self.hide()
        watcher_window.show()

    def slot_quick_analyzer(self):
        quick_analyzer_window = RaQuickAnalyzerWindow()
        quick_analyzer_window.signal_close.connect(self.show)
        self.hide()
        quick_analyzer_window.show()

    class RaStartupWindowCentralWidget(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setLayout(QVBoxLayout())

            passive_group_box = QGroupBox("Passive Analyzer")
            active_group_box = QGroupBox("Active Converter")
            watch_mode_group_box = QGroupBox("Watch Mode and Quick Analyzer")

            self.__passive_button = QPushButton("Passive Analyzer")
            self.__active_button = QPushButton("Active Converter")
            self.__watch_mode_button = QPushButton("Watch Mode")
            self.__quick_analyzer_button = QPushButton("Quick Analyzer")

            passive_group_box.setLayout(QVBoxLayout())
            passive_group_box.layout().addWidget(self.__passive_button)

            active_group_box.setLayout(QVBoxLayout())
            active_group_box.layout().addWidget(self.__active_button)

            watch_mode_group_box.setLayout(QHBoxLayout())
            watch_mode_group_box.layout().addWidget(self.__watch_mode_button)
            watch_mode_group_box.layout().addWidget(self.__quick_analyzer_button)

            self.layout().addWidget(passive_group_box)
            self.layout().addWidget(active_group_box)
            self.layout().addWidget(watch_mode_group_box)

        @property
        def passive_button(self):
            return self.__passive_button

        @property
        def active_button(self):
            return self.__active_button

        @property
        def watch_mode_button(self):
            return self.__watch_mode_button

        @property
        def quick_analyzer_button(self):
            return self.__quick_analyzer_button
