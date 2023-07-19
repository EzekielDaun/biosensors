import logging
import os
import pathlib
import sys
from datetime import datetime
from queue import Queue

import numpy as np
import pyqtgraph as pg
from numpy.typing import NDArray
from pyqtgraph import ImageView, PlotItem, ScatterPlotItem
from PySide6.QtCore import QFileSystemWatcher, Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent, QTextCursor, QTransform
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ..core.lib import SweepFitResult
from ..core.passive_tools import read_mat
from ..widgets.lib.ra_drop_widgets import RaDropLineEdit, RaDropPushButton

logger = logging.getLogger(__name__)


DEFAULT_TEMP_FILENAME = ".ra_temp.npz"
DEFAULT_RESULT_FILENAME = "ra_peaks.npz"
DEFAULT_SPECTROGRAM_FILENAME = "ra_spectrograms.npz"

NP_PEAK_KEY = "sweeps"
NP_SPECTROGRAM_KEY = "spectrograms"
NP_WAVELENGTH_KEY = "wavelength"


class RaWatcherWindow(QMainWindow):
    signal_close = Signal()
    signal_write = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(1440, 810)

        self.__central_widget = self.RaWatcherWindowCentralWidget()
        self.__central_widget.signal_start_watch.connect(self.slot_start_watch)
        self.__central_widget.signal_stop_watch.connect(self.slot_stop_watch)
        self.setCentralWidget(self.__central_widget)

        self.__text_browser = QTextBrowser()
        dock_widget = QDockWidget()
        dock_widget.setWidget(self.__text_browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

        # redirect logging
        sys.stdout = self
        sys.stderr = self
        self.__log_handler = logging.StreamHandler(self)
        self.__log_handler.setFormatter(logging.getLogger().handlers[0].formatter)
        self.__log_handler.setLevel(logging.getLogger().handlers[0].level)
        logging.getLogger().addHandler(self.__log_handler)
        self.signal_write.connect(self.slot_write)

    def write(self, text):
        self.signal_write.emit(text)

    def flush(self):
        pass

    @Slot(str)
    def slot_write(self, text: str):
        self.__text_browser.moveCursor(QTextCursor.End)  # type: ignore
        self.__text_browser.insertPlainText(text)
        self.__text_browser.ensureCursorVisible()

    def closeEvent(self, event: QCloseEvent):
        self.signal_close.emit()
        if self.__central_widget.watch_button.isChecked():
            self.slot_stop_watch(self.__central_widget.path_line_edit.text())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        logging.getLogger().removeHandler(self.__log_handler)
        return super().closeEvent(event)

    # slots
    def slot_start_watch(self, dir: str):
        # remove np temp file if exists
        if os.path.exists(np_tmp_path := os.path.join(dir, DEFAULT_TEMP_FILENAME)):
            os.remove(np_tmp_path)

        # clear table widget
        self.__central_widget.table_widget.setRowCount(0)

        # clear tab widget
        self.__central_widget.spectrogram_tab_widget.clear()

        # initialize file list
        self.__files_temp = {
            p for p in os.listdir(dir) if pathlib.Path(p).suffix == ".mat"
        }

        # initialize a queue
        self.__queue: Queue[str] = Queue()

        # start a watcher
        self.__watcher = QFileSystemWatcher()
        self.__watcher.addPath(dir)
        self.__watcher.directoryChanged.connect(self.slot_dir_changed)

    def slot_stop_watch(self, dir: str):
        self.__watcher.directoryChanged.disconnect(self.slot_dir_changed)
        self.__watcher.deleteLater()
        self.__queue.join()

        sweeps = np.load(os.path.join(dir, DEFAULT_TEMP_FILENAME), allow_pickle=True)[
            NP_PEAK_KEY
        ]
        np.savez_compressed(os.path.join(dir, DEFAULT_RESULT_FILENAME), sweeps=sweeps)

        np.savez_compressed(
            os.path.join(dir, DEFAULT_SPECTROGRAM_FILENAME),
            spectrograms=self.__spectrograms,
            wavelength=self.__wavelength,
        )

        # remove np temp file if exists
        if os.path.exists(np_tmp_path := os.path.join(dir, DEFAULT_TEMP_FILENAME)):
            os.remove(np_tmp_path)

    def slot_dir_changed(self, dir: str):
        files_now = {p for p in os.listdir(dir) if pathlib.Path(p).suffix == ".mat"}
        for f in sorted(
            files_now.difference(self.__files_temp),
            key=lambda x: os.path.getmtime(os.path.join(dir, x)),
        ):
            logger.info(f"{f}")
            self.__queue.put(os.path.join(dir, f))
        self.update_new_files_in_queue()
        self.__files_temp.update(files_now)

    def update_new_files_in_queue(self):
        while not self.__queue.empty():
            path = self.__queue.get()

            row_index = self.__central_widget.table_widget.rowCount()
            self.__central_widget.table_widget.insertRow(row_index)
            self.__central_widget.table_widget.setItem(
                row_index, 0, QTableWidgetItem(str(datetime.now()))
            )
            self.__central_widget.table_widget.setItem(
                row_index, 1, QTableWidgetItem(os.path.basename(path))
            )

            power, wavelength = read_mat(path)
            wavelength *= 1e9
            if not os.path.exists(
                temp_path := os.path.join(
                    pathlib.Path(path).parent, DEFAULT_TEMP_FILENAME
                )
            ):  # the first file
                self.__wavelength = wavelength

                self.__spectrograms: NDArray = np.array([power], ndmin=3)
                self.__spectrograms = self.__spectrograms.swapaxes(0, 1)

                sweeps = np.array(
                    [SweepFitResult.from_data(channel, wavelength) for channel in power]
                )
                np.savez_compressed(temp_path, sweeps=sweeps)

                for i, channel in enumerate(power):
                    name = f"Channel {i+1}"
                    self.__central_widget.spectrogram_tab_widget.addTab(
                        RaWatcherWindowSpectrogramPlotWidget(name), name
                    )
            else:
                self.__spectrograms = np.append(
                    self.__spectrograms,
                    np.array([power], ndmin=3).swapaxes(0, 1),
                    axis=1,
                )
                old_sweeps = np.load(temp_path, allow_pickle=True)[NP_PEAK_KEY]
                sweeps = np.array(
                    [
                        np.append(
                            channel, [SweepFitResult.from_data(power[i], wavelength)]  # type: ignore
                        )
                        for i, channel in enumerate(old_sweeps)
                    ]
                )
                np.savez_compressed(
                    temp_path,
                    sweeps=sweeps,
                )

            for i, channel in enumerate(power):
                tr = QTransform()
                tr.translate(-0.5, min(wavelength))
                tr.scale(1, (max(wavelength) - min(wavelength)) / len(wavelength))
                spectrogram_widget: RaWatcherWindowSpectrogramPlotWidget = (
                    self.__central_widget.spectrogram_tab_widget.widget(i)
                )  # type: ignore
                spectrogram_widget.image_view.setImage(
                    self.__spectrograms[i], transform=tr
                )

                current_index = self.__spectrograms[i].shape[0] - 1
                sweep = SweepFitResult.from_data(channel, wavelength)
                for p in sweep.get_peaks():
                    spectrogram_widget.scatter_plot_item.addPoints(
                        [current_index], [p[0]]
                    )

            self.__queue.task_done()

    class RaWatcherWindowCentralWidget(QWidget):
        signal_start_watch = Signal(str)
        signal_stop_watch = Signal(str)

        def __init__(self):
            super().__init__()

            self.path_line_edit = RaDropLineEdit()
            self.path_line_edit.signal_drop.connect(  # type: ignore
                self.path_line_edit.setText
            )

            self.path_select_button = RaDropPushButton("Select")
            self.path_select_button.signal_drop.connect(  # type: ignore
                self.path_line_edit.setText
            )

            self.watch_button = QPushButton("Watch")
            self.watch_button.setCheckable(True)

            self.table_widget = QTableWidget()
            self.table_widget.setColumnCount(2)
            self.table_widget.setHorizontalHeaderLabels(["Time", "Name"])
            self.table_widget.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            self.table_widget.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )

            self.spectrogram_tab_widget = QTabWidget()

            # layout widgets
            self.setLayout(QHBoxLayout())
            splitter = QSplitter(Qt.Orientation.Horizontal)

            path_layout = QHBoxLayout()
            path_layout.addWidget(self.path_line_edit)
            path_layout.addWidget(self.path_select_button)

            left_widget = QWidget()
            left_widget.setLayout(QVBoxLayout())
            left_widget.layout().addLayout(path_layout)  # type: ignore
            left_widget.layout().addWidget(self.watch_button)
            left_widget.layout().addWidget(self.table_widget)

            splitter.addWidget(left_widget)
            splitter.setStretchFactor(0, 0)
            splitter.addWidget(self.spectrogram_tab_widget)
            splitter.setStretchFactor(1, 1)

            self.layout().addWidget(splitter)

            # connect signals
            self.path_select_button.clicked.connect(self.slot_select_path)
            self.watch_button.toggled.connect(self.slot_watch_toggled)

        def slot_select_path(self):
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
            self.path_line_edit.setText(path)

        def slot_watch_toggled(self, checked: bool):
            if not checked:
                self.path_line_edit.setReadOnly(False)
                self.path_select_button.setDisabled(False)
                self.watch_button.setText("Watch")
                self.signal_stop_watch.emit(self.path_line_edit.text())
            elif not os.path.exists(path := self.path_line_edit.text()):
                logger.warning(f'Path "{path}" does not exist.')
                self.path_line_edit.setReadOnly(False)
                self.path_select_button.setDisabled(False)

                self.watch_button.blockSignals(True)
                self.watch_button.setChecked(False)
                self.watch_button.blockSignals(False)
            elif not (dir_set := set(os.listdir(path))).issubset(
                set([".DS_Store", DEFAULT_TEMP_FILENAME])
            ):
                logger.warning(f'Directory "{path}" is not empty: {dir_set}')
                self.watch_button.blockSignals(True)
                self.watch_button.setChecked(False)
                self.watch_button.blockSignals(False)
            else:
                self.path_line_edit.setReadOnly(True)
                self.path_select_button.setDisabled(True)
                self.watch_button.setText("Watching new files...")
                self.signal_start_watch.emit(path)


class RaWatcherWindowSpectrogramPlotWidget(QWidget):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize members
        self.__plot_item = PlotItem()
        self.__plot_item.getAxis("bottom").setLabel("Sweep Number")
        self.__plot_item.getAxis("left").setLabel("Wavelength", units="m")
        self.__plot_item.getAxis("left").setScale(1e-9)
        self.__plot_item.setTitle(f"{name} Spectrogram")

        self.__image_view = ImageView(view=self.__plot_item)
        self.__image_view.ui.roiBtn.hide()
        self.__image_view.ui.menuBtn.hide()
        self.__image_view.getView().invertY(False)
        self.__image_view.getView().setAspectLocked(False)
        self.__image_view.setColorMap(pg.colormap.getFromMatplotlib("inferno"))

        self.__scatter_plot_item = ScatterPlotItem()
        self.__plot_item.addItem(self.__scatter_plot_item)

        # layout widgets
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.__image_view)

    @property
    def plot_item(self):
        return self.__plot_item

    @property
    def image_view(self):
        return self.__image_view

    @property
    def scatter_plot_item(self):
        return self.__scatter_plot_item
