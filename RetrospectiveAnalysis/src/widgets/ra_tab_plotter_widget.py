import logging

import os


import numpy as np

from matplotlib.ticker import FuncFormatter


from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import QThread, Slot, Signal

from .ra_figure_widget import RaFigureWidget
from ..core.retrospective_analysis import read_mat, get_lorentzian_peaks, lorentzian
from ..core.retrospective_analysis import RetrospectiveAnalyzer as Analyzer

logger = logging.getLogger(__name__)


class __RaTabPlotterWorkerBase(QThread):
    """Base class for the tab plotter worker thread to do heavy work

    !!Do not use directly!! Overload this for customizations
    """

    def __init__(self, *args, **kwargs):
        """pass necessary parameters to initialize a worker instance"""
        super().__init__()
        return

    def run(self):
        """Actual work function to be implemented by subclass"""
        raise NotImplementedError


class __RaTabPlotterBase(QTabWidget):
    """Base class for the tab plotter

    !!Do not use directly!! Overload this for customizations

    Note: this class is an implicit singleton due to Qt signal mechanism. The derived classes should override the class attribute `__signal_work_start` to avoid getting parent class' signal.
    """

    __signal_work_start = Signal()

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.__signal_work_start.connect(self.slot_work_start)

    @Slot()
    def slot_work_start(self):
        raise NotImplementedError
        self.__worker = __RaTabPlotterWorkerBase()
        self.__worker.finished.connect(self.slot_work_done)  # type: ignore
        self.__worker.start()

    @Slot()
    def slot_work_done(self):
        raise NotImplementedError
        self.__worker.finished.disconnect(self.slot_work_done)  # type: ignore
        result = self.__worker._sample_result__
        logger.debug(f"{self.__class__.__name__}: Work done with result: {result}")
        del self.__worker


class RaFilePlotterWorker(__RaTabPlotterWorkerBase):
    def __init__(self, path: str):
        super().__init__()
        self.__path = path

    @property
    def powers(self):
        return self.__powers

    @property
    def wavelengths(self):
        return self.__wavelengths * 1e9

    def run(self):
        logger.debug(f"Analyzing {self.__path}")
        self.__powers, self.__wavelengths = read_mat(self.__path)


class RaFilePlotter(__RaTabPlotterBase):
    __signal_work_start = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__signal_work_start.connect(self.slot_work_start)

        self.__current_tab_index: int = 0

        self.__current_file_basename: str | None = None

    def plot_file(self, file_path: str):
        self.__current_file_basename = os.path.basename(file_path)
        self.__signal_work_start.emit(file_path)

    @Slot(str)
    def slot_work_start(self, path: str):
        self.__worker = RaFilePlotterWorker(path)
        self.__worker.finished.connect(self.slot_work_done)  # type: ignore
        self.__worker.start()

    @Slot()
    def slot_work_done(self):
        self.__worker.finished.disconnect(self.slot_work_done)  # type: ignore

        # clear previous plots
        self.__current_tab_index = self.currentIndex()
        for index in range(self.count()):
            self.widget(index).deleteLater()
        self.clear()

        # make new plots
        for i, power in enumerate(self.__worker.powers):
            figure_widget = RaFigureWidget()
            axes = figure_widget.figure.subplots()
            axes.plot(self.__worker.wavelengths, power)

            axes.set_title(f"{self.__current_file_basename}")
            axes.set_xlabel("Wavelength")
            axes.set_ylabel("Power")
            figure_widget.figure.set_tight_layout(True)
            figure_widget.figure_canvas.show()
            self.addTab(figure_widget, f"Power {str(i + 1)}")

            peaks = get_lorentzian_peaks(power, self.__worker.wavelengths, 0.2)
            for j, peak in enumerate(peaks):
                x0, y0, _i, gamma = peak
                xs = np.linspace(x0 - 5 * gamma, x0 + 5 * gamma, 101)
                ys = lorentzian(xs, x0, y0, _i, gamma)
                axes.plot(xs, ys, "-")
        self.__worker.deleteLater()

        if self.__current_tab_index < self.count():
            self.setCurrentIndex(self.__current_tab_index)


class RaFolderPlotterSpectrogramWorker(__RaTabPlotterWorkerBase):
    def __init__(self, analyzer: Analyzer, channels: list[int], step: int):
        super().__init__()
        self.__analyzer = analyzer
        self.__channels = channels
        self.__step = step

    @property
    def spectrogram_dict(self):
        return self.__spectrogram_dict

    def run(self):
        self.__spectrogram_dict = self.__analyzer.get_spectrograms(
            self.__channels, self.__step
        )


class RaFolderPlotter(__RaTabPlotterBase):
    __signal_spectrograms_work_start = Signal()
    signal_spectrograms_work_done = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__signal_spectrograms_work_start.connect(
            self.__slot_spectrograms_work_start
        )

        # an analyer should be initialized outside and passed into this class
        self.analyzer: Analyzer = None  # type: ignore

    def plot_spectrograms(
        self,
        channels: list[int],
        step: int,
        x_tick_number: int,
        y_tick_number: int,
        power_unit: str,
    ):
        if self.analyzer is None:
            raise RuntimeError("Analyzer is not initialized")
        else:
            # clear previous plots
            for index in range(self.count()):
                self.widget(index).deleteLater()
            self.clear()

            self.__channels = channels
            self.__step = step
            self.__x_tick_step = int(len(self.analyzer.timestamps) / x_tick_number)
            self.__y_tick_step = int(len(self.analyzer.wavelengths) / y_tick_number)
            self.__power_unit = power_unit
            self.__signal_spectrograms_work_start.emit()

    @Slot()
    def __slot_spectrograms_work_start(self):
        self.__worker = RaFolderPlotterSpectrogramWorker(
            self.analyzer, self.__channels, self.__step
        )
        self.__worker.finished.connect(self.__slot_spectrograms_work_done)  # type: ignore
        self.__worker.start()
        self.signal_spectrograms_work_done.emit(False)

    @Slot()
    def __slot_spectrograms_work_done(self):
        self.__worker.finished.disconnect(self.__slot_spectrograms_work_done)  # type: ignore

        # make new plots
        x_labels = np.vectorize(lambda x: "{:.5g}".format(x))(
            self.analyzer.timestamps[:: self.__step]
        )
        y_labels = np.vectorize(lambda x: "{:.5g}".format(x))(
            self.analyzer.wavelengths[::-1]
        )
        x_formatter = FuncFormatter(
            lambda x, _: x_labels[int(x)] if int(x) in range(len(x_labels)) else None
        )
        y_formatter = FuncFormatter(
            lambda y, _: y_labels[int(y)] if int(y) in range(len(y_labels)) else None
        )
        for k, v in self.__worker.spectrogram_dict.items():
            figure_widget = RaFigureWidget()
            ax = figure_widget.figure.subplots()
            image = ax.imshow(v, cmap="inferno")

            ax.set_xticks(
                list(range(len(x_labels)))[:: self.__x_tick_step],
                x_labels[:: self.__x_tick_step],
            )
            ax.set_xlabel("Time (minutes)")
            ax.xaxis.set_major_formatter(x_formatter)

            ax.set_yticks(
                list(range(len(y_labels)))[:: self.__y_tick_step],
                y_labels[:: self.__y_tick_step],
            )
            ax.set_ylabel("Wavelength (nm)")
            ax.yaxis.set_major_formatter(y_formatter)

            ax.set_title(f"Power {k+1} Spectrogram")
            ax.axis("auto")

            color_bar = figure_widget.figure.colorbar(image, orientation="horizontal")
            color_bar.set_label(f"Power ({self.__power_unit})")

            figure_widget.figure.set_tight_layout(True)
            figure_widget.figure_canvas.show()
            self.addTab(figure_widget, f"Power {k+1}")

        del self.__worker
        self.signal_spectrograms_work_done.emit(True)
