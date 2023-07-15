import logging
import os
import sys
from itertools import cycle

import numpy as np
import pyqtgraph as pg
from numpy.typing import NDArray
from pyqtgraph import ImageView, PlotItem
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent, QTextCursor, QTransform
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from scipy.io import savemat

from ..core.lib import SweepFitResult, group_peaks, peaks_to_traces
from ..widgets.lib.ra_plot_curve_item import RaPlotCurveItem
from .ra_watcher_window import (
    DEFAULT_RESULT_FILENAME,
    DEFAULT_SPECTROGRAM_FILENAME,
    NP_PEAK_KEY,
    NP_SPECTROGRAM_KEY,
    NP_WAVELENGTH_KEY,
)

logger = logging.getLogger(__name__)


class RaQuickAnalyzerWindow(QMainWindow):
    signal_close = Signal()
    signal_write = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(1440, 810)

        self.__central_widget = self.RaQuickAnalyzerWindowCentralWidget()
        self.setCentralWidget(self.__central_widget)

        self.__text_browser = QTextBrowser()
        dock_widget = QDockWidget()
        dock_widget.setWidget(self.__text_browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

        # connections
        self.__central_widget.signal_analyze.connect(self.__slot_analyze)
        self.__central_widget.signal_save.connect(self.__slot_save)

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
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        logging.getLogger().removeHandler(self.__log_handler)
        return super().closeEvent(event)

    # slots
    def __slot_analyze(self, peak_file_path: str, spectrogram_file_path: str):
        self.__central_widget.tab_widget.clear()

        self.__sweep_2d: list[list[SweepFitResult]] = np.load(
            peak_file_path, allow_pickle=True
        )[NP_PEAK_KEY]
        spectrograms = np.load(spectrogram_file_path, allow_pickle=True)[
            NP_SPECTROGRAM_KEY
        ]
        wavelength = np.load(spectrogram_file_path, allow_pickle=True)[
            NP_WAVELENGTH_KEY
        ]

        for i, channel in enumerate(spectrograms):
            channel: NDArray
            plot_widget = RaQuickAnalyzerPlotWidget(f"Channel {i+1}")

            tr = QTransform()
            tr.translate(-0.5, min(wavelength))
            tr.scale(1, (max(wavelength) - min(wavelength)) / len(wavelength))

            plot_widget.image_view.setImage(channel, transform=tr)
            self.__central_widget.tab_widget.addTab(plot_widget, f"Channel {i+1}")

            sweeps = self.__sweep_2d[i]
            peaks = [sweep.get_peaks() for sweep in sweeps]
            traces, fsr = peaks_to_traces(peaks)

            color_palette = cycle(["light green", "blue"])
            x0 = 0
            for trace in traces:
                plot_widget.add_curve_item(
                    RaPlotCurveItem(
                        fsr,
                        x=np.linspace(x0, x0 + len(trace) - 1, len(trace)),
                        y=trace,
                        pen={
                            "color": next(color_palette),
                            "width": 5,
                            "cosmetic": True,
                        },
                    )
                )
                x0 += len(trace)

        self.__central_widget.save_button.setEnabled(True)

    def __slot_save(self, dir: str):
        peak_shift_path = os.path.join(dir, "peak_shifts.mat")
        peaks_path = os.path.join(dir, "peaks.mat")
        all_tabs: list[RaQuickAnalyzerPlotWidget] = [  # type: ignore
            self.__central_widget.tab_widget.widget(i)
            for i in range(self.__central_widget.tab_widget.count())
        ]

        # save peak shifts
        savemat(
            peak_shift_path,
            {
                (tab.name).replace(" ", "_").lower() + "_peakWL_list": tab.full_trace
                for tab in all_tabs
            },
        )

        # save all fitted peaks and peak trace indices
        savemat(
            peaks_path,
            {
                "channel"
                + str(i + 1): np.array(
                    [s.get_peaks() for s in self.__sweep_2d[i]], dtype="object"
                )
                for i in range(len(self.__sweep_2d))
            }
            | {
                "channel"
                + str(i + 1)
                + "_peak_trace_indices": np.array(
                    group_peaks(
                        [[p[0] for p in ps] for ps in [s.get_peaks() for s in self.__sweep_2d[i]]],  # type: ignore
                        all_tabs[i].full_trace,
                    ),
                    dtype="object",
                )
                for i in range(len(self.__sweep_2d))
            },
        )

    class RaQuickAnalyzerWindowCentralWidget(QWidget):
        signal_analyze = Signal(str, str)
        signal_save = Signal(str)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setLayout(QHBoxLayout())

            # widgets
            self.__peak_file_path_line_edit = QLineEdit()
            self.__peak_file_select_button = QPushButton("Select RA Peak File")

            self.__spectrogram_file_path_line_edit = QLineEdit()
            self.__spectrogram_file_select_button = QPushButton(
                "Select RA Spectrogram File"
            )

            self.__analyze_button = QPushButton("Analyze")
            self.__save_button = QPushButton("Save Result")
            self.__save_button.setDisabled(True)

            self.__tab_widget = QTabWidget()

            # layout
            grid_layout = QGridLayout()
            grid_layout.addWidget(self.__peak_file_path_line_edit, 0, 0)
            grid_layout.addWidget(self.__peak_file_select_button, 0, 1)
            grid_layout.addWidget(self.__spectrogram_file_path_line_edit, 1, 0)
            grid_layout.addWidget(self.__spectrogram_file_select_button, 1, 1)

            left_widget = QWidget()
            left_widget.setLayout(QVBoxLayout())
            left_widget.layout().addLayout(grid_layout)  # type: ignore
            left_widget.layout().addWidget(self.__analyze_button)
            left_widget.layout().addWidget(self.__save_button)
            left_widget.layout().addSpacerItem(  # type: ignore
                QSpacerItem(
                    0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
                )
            )

            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.addWidget(left_widget)
            splitter.setStretchFactor(0, 0)
            splitter.addWidget(self.__tab_widget)
            splitter.setStretchFactor(1, 1)

            self.layout().addWidget(splitter)

            # connections
            self.__peak_file_select_button.clicked.connect(self.__slot_peak_file_select)
            self.__spectrogram_file_select_button.clicked.connect(
                self.__slot_spectrogram_file_select
            )
            self.__analyze_button.clicked.connect(self.__slot_analyze)
            self.__save_button.clicked.connect(self.__slot_save)

        @property
        def tab_widget(self):
            return self.__tab_widget

        @property
        def save_button(self):
            return self.__save_button

        def __is_valid(self):
            return os.path.isfile(
                self.__peak_file_path_line_edit.text()
            ) and os.path.isfile(self.__spectrogram_file_path_line_edit.text())

        # slots
        def __slot_peak_file_select(self):
            file_path = QFileDialog.getOpenFileName(
                self, "Select RA Peak", filter=f"RA Peak ({DEFAULT_RESULT_FILENAME})"
            )
            self.__peak_file_path_line_edit.setText(file_path[0])

        def __slot_spectrogram_file_select(self):
            file_path = QFileDialog.getOpenFileName(
                self,
                "Select RA Spectrogram",
                filter=f"RA Spectrogram ({DEFAULT_SPECTROGRAM_FILENAME})",
            )
            self.__spectrogram_file_path_line_edit.setText(file_path[0])

        def __slot_analyze(self):
            if self.__is_valid():
                self.signal_analyze.emit(
                    self.__peak_file_path_line_edit.text(),
                    self.__spectrogram_file_path_line_edit.text(),
                )

        def __slot_save(self):
            if dir := QFileDialog.getExistingDirectory():
                self.signal_save.emit(dir)


class RaQuickAnalyzerPlotWidget(QWidget):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__name = name
        self.__curve_items: list[RaPlotCurveItem] = []

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

        # layout widgets
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.__image_view)

    @property
    def plot_item(self):
        return self.__plot_item

    @property
    def curve_items(self):
        return self.__curve_items

    @property
    def image_view(self):
        return self.__image_view

    @property
    def name(self):
        return self.__name

    def add_curve_item(self, curve_item: RaPlotCurveItem):
        self.__plot_item.addItem(curve_item)
        self.__curve_items.append(curve_item)

    @property
    def full_trace(self):
        return np.concatenate([curve_item.yData for curve_item in self.__curve_items])  # type: ignore
