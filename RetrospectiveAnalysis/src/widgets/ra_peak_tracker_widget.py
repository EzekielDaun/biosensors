import logging
import os
from itertools import cycle
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph import ImageView, PlotCurveItem, PlotItem
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget
from scipy.io import savemat

from ..core.lib import group_peaks
from ..core.passive_tools import PassiveAnalyzer as Analyzer
from ..uic.ra_peak_tracker_tab_setting_widget import Ui_PeakTrackerTabSettingWidget
from .ra_figure_widget import RaFigureWidget

logger = logging.getLogger(__name__)


class RaPlotCurveItem(PlotCurveItem):
    def __init__(self, fsr: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__fsr = fsr
        _, self.__y = self.getData()

    def mouseDragEvent(self, ev):
        if (
            ev.button() != Qt.MouseButton.LeftButton
            and ev.button() != Qt.MouseButton.RightButton
        ):
            ev.ignore()
            return

        if ev.isStart():
            _, y = self.getData()
            self.__drag_y_offsets = y - ev.buttonDownPos().y()
        elif ev.isFinish():
            return

        x, y = self.getData()
        if ev.button() == Qt.MouseButton.LeftButton:
            # left click, free drag
            self.updateData(x, ev.pos().y() + self.__drag_y_offsets)
        elif ev.button() == Qt.MouseButton.RightButton:
            # magnet effect, attach to the nearest fsr
            y_ideal = ev.pos().y() + self.__drag_y_offsets
            y_diff = y_ideal - self.__y
            y_diff = np.round(y_diff / self.__fsr) * self.__fsr
            y_final = self.__y + y_diff
            self.updateData(x, y_final)
        ev.accept()


class RaPeakTrackerWidget(QWidget):
    class __Worker(QThread):
        def __init__(
            self,
            analyzer: Analyzer,
            channels: set[int],
            start_stop_step: tuple[int, Optional[int], int],
            r2_threshold: float,
            max_n100dBm_points: int,
        ):
            super().__init__()
            self.__analyzer = analyzer
            self.__channels = channels
            self.__start_stop_step = start_stop_step
            self.__r2_threshold = r2_threshold
            self.__max_n100dBm_points = max_n100dBm_points

        def run(self):
            self.__all_traces, self.__all_peaks = self.__analyzer.analyze(
                self.__channels,
                self.__start_stop_step,
                self.__r2_threshold,
                self.__max_n100dBm_points,
            )

        @property
        def all_traces(self):
            return self.__all_traces

        @property
        def all_peaks(self):
            return self.__all_peaks

    class __FSR_ER_Q_Worker(QThread):
        def __init__(
            self,
            analyzer: Analyzer,
            channels: set[int],
            start_stop_step: tuple[int, Optional[int], int],
            r2_threshold: float,
            max_n100dBm_points: int,
        ):
            super().__init__()
            self.__analyzer = analyzer
            self.__channels = channels
            self.__start_stop_step = start_stop_step
            self.__r2_threshold = r2_threshold
            self.__max_n100dBm_points = max_n100dBm_points

        def run(self):
            self.__fsr_er_q_dict = self.__analyzer.analyze_fsr_er_q(
                self.__channels,
                self.__start_stop_step,
                self.__r2_threshold,
                self.__max_n100dBm_points,
            )

        @property
        def fsr_er_q_dict(self):
            return self.__fsr_er_q_dict

    class __Tab(QWidget):
        def __init__(
            self,
            power_index: int,
            traces: list[list[float]],
            fsr: float,
            analyzer: Analyzer,
            start_stop_step: tuple[int, Optional[int], int],
            time_unit: str,
            wavelength_unit: str,
            power_unit: str,
            parent=None,
        ):
            super().__init__(parent)
            self.__ui = Ui_PeakTrackerTabSettingWidget()
            self.__ui.setupUi(self)

            self.__name = f"Power {power_index+1}"
            self.__power_index = power_index
            self.__traces = traces
            self.__fsr = fsr
            self.__timestamps = analyzer.timestamps[
                start_stop_step[0] : start_stop_step[1] : start_stop_step[2]
            ]
            self.__start_stop_step = start_stop_step
            self.__analyzer = analyzer
            self.__time_unit = time_unit
            self.__power_unit = power_unit
            self.__wavelength_unit = wavelength_unit

            self.__plot_item = PlotItem()
            self.__plot_item.getAxis("bottom").setLabel("Sweep Number")
            self.__plot_item.getAxis("left").setLabel("Wavelength", units="m")
            self.__plot_item.getAxis("left").setScale(1e-9)
            self.__plot_item.setTitle(f"{self.__name} Peak Shift")

            self.__image_view = ImageView(view=self.__plot_item)
            self.__image_view.ui.roiBtn.hide()
            self.__image_view.ui.menuBtn.hide()
            self.__image_view.getView().invertY(False)
            self.__image_view.getView().setAspectLocked(False)
            self.__image_view.setColorMap(pg.colormap.getFromMatplotlib("inferno"))

            self.__figure_widget = RaFigureWidget()
            self.__ui.splitter.addWidget(self.__image_view)
            self.__ui.splitter.setStretchFactor(self.__ui.splitter.count() - 1, 1)

            self.__ui.plotPeakOffsetButton.clicked.connect(self.__slot_plot_peak_offset)  # type: ignore
            self.__ui.plotOverlayButton.clicked.connect(self.__slot_plot_overlay)  # type: ignore
            self.__ui.plotOffsetSpectrogramButton.clicked.connect(self.__slot_plot_offset_spectrogram)  # type: ignore

            image = self.__analyzer.get_spectrograms({self.__power_index})[
                self.__power_index
            ].T[:, ::-1]
            self.__image_view.setImage(image)

            tr = QTransform()
            tr.translate(
                -0.5,
                -0.5 * max(np.diff(self.__analyzer.wavelengths))
                + float(np.min(self.__analyzer.wavelengths)),
            )
            tr.scale(
                1,
                (
                    float(np.max(self.__analyzer.wavelengths))
                    - float(np.min(self.__analyzer.wavelengths))
                )
                / len(self.__analyzer.wavelengths),
            )

            self.__image_view.getImageItem().setTransform(tr)
            self.__image_view.getView().autoRange()

            ax = self.__figure_widget.figure.subplots(1, 1)
            ax.set_title(f"{self.__name} Peak Shift")
            ax.set_xlabel(f"Time ({self.__time_unit})")
            ax.set_ylabel(f"Wavelength ({self.__wavelength_unit})")

            color_palette = cycle(["light green", "grey"])
            x0 = 0
            for trace in self.__traces:
                if len(trace) <= 1:
                    pass
                else:
                    item = RaPlotCurveItem(
                        fsr=self.__fsr,
                        x=np.linspace(x0, x0 + len(trace) - 1, len(trace)),
                        y=trace,
                        pen={
                            "color": next(color_palette),
                            "width": 5,
                            "cosmetic": True,
                        },
                    )
                    self.__plot_item.addItem(item)
                x0 += len(trace)

        @property
        def name(self):
            return self.__name

        @property
        def power_index(self):
            return self.__power_index

        @property
        def full_trace(self):
            ret = np.array([np.NAN] * sum(map(len, self.__traces)))
            for item in self.__plot_item.listDataItems():
                xs, ys = item.getData()
                for i, x in enumerate(xs):
                    ret[int(np.round(x))] = ys[i]

            return ret

        @Slot()
        def __slot_plot_peak_offset(self):
            plt.close("all")
            fig, ax = plt.subplots()

            ys = self.full_trace - self.full_trace[0]

            ax.plot(self.__timestamps[: len(ys)], ys)
            ax.set_xlabel(f"Time ({self.__time_unit})")
            ax.set_ylabel(f"Peak Shift ({self.__wavelength_unit})")
            fig.set_size_inches(8, 5)
            ax.axis("auto")
            title = f"{self.__name} Peak Offset"
            ax.set_title(title)
            if self.__ui.autoSaveCheckBox.isChecked():
                plt.savefig(title.replace(" ", "_").lower() + ".png")
            plt.show()

        @Slot()
        def __slot_plot_overlay(self):
            plt.close("all")
            fig, ax = plt.subplots()

            spectrogram = self.__analyzer.get_spectrograms({self.__power_index})[
                self.__power_index
            ][
                :,
                self.__start_stop_step[0] : self.__start_stop_step[
                    1
                ] : self.__start_stop_step[2],
            ]
            ys = self.full_trace
            ys -= min(self.__analyzer.wavelengths)
            ys /= max(self.__analyzer.wavelengths) - min(self.__analyzer.wavelengths)
            ys *= len(self.__analyzer.wavelengths)

            img = ax.imshow(np.flip(spectrogram, 0), cmap="inferno", origin="lower")
            color_bar = fig.colorbar(img, orientation="horizontal")
            color_bar.set_label(f"Power ({self.__power_unit})")

            ax.plot(ys)
            ax.set_xlabel(f"Time ({self.__time_unit})")
            ax.set_xticks(
                [0, len(ys) - 1], [0, f"{self.__analyzer.timestamps[-1]:.5g}"]
            )
            ax.set_ylabel(f"Wavelength ({self.__wavelength_unit})")
            ax.set_yticks(
                list(range(len(self.__analyzer.wavelengths)))[
                    :: int(len(self.__analyzer.wavelengths) / 7)
                ],
                list(
                    map(
                        lambda x: f"{x:.5g}",
                        self.__analyzer.wavelengths[
                            :: int(len(self.__analyzer.wavelengths) / 7)
                        ],
                    )
                ),
            )
            title = f"{self.__name} Peak Shift Overlay"
            ax.set_title(title)
            fig.set_size_inches(8, 5)
            ax.axis("auto")
            if self.__ui.autoSaveCheckBox.isChecked():
                plt.savefig(title.replace(" ", "_").lower() + ".png")
            plt.show()

        @Slot()
        def __slot_plot_offset_spectrogram(self):
            plt.close("all")

            trace_ax = plt.subplot(2, 1, 1)
            ys = self.full_trace
            ys -= ys[0]
            trace_ax.plot(self.__timestamps[: len(ys)], ys)
            trace_ax.set_xlabel(f"Time ({self.__time_unit})")
            trace_ax.set_ylabel(f"Wavelength ({self.__wavelength_unit})")
            trace_ax.set_title(f"{self.__name} Peak Offset")

            spectrogram_ax = plt.subplot(2, 1, 2)
            spectrogram = self.__analyzer.get_spectrograms({self.__power_index})[
                self.__power_index
            ][
                :,
                self.__start_stop_step[0] : self.__start_stop_step[
                    1
                ] : self.__start_stop_step[2],
            ]
            ys = self.full_trace
            ys -= min(self.__analyzer.wavelengths)
            ys /= max(self.__analyzer.wavelengths) - min(self.__analyzer.wavelengths)
            ys *= len(self.__analyzer.wavelengths)
            img = spectrogram_ax.imshow(
                np.flip(spectrogram, 0),
                cmap="inferno",
                origin="lower",
                aspect="auto",
            )
            spectrogram_ax.autoscale()
            spectrogram_ax.set_xlabel(f"Time ({self.__time_unit})")
            spectrogram_ax.set_xticks(
                [0, len(ys) - 1], [0, f"{self.__analyzer.timestamps[-1]:.5g}"]
            )
            spectrogram_ax.set_ylabel(f"Wavelength ({self.__wavelength_unit})")
            spectrogram_ax.set_yticks(
                list(range(len(self.__analyzer.wavelengths)))[
                    :: int(len(self.__analyzer.wavelengths) / 7)
                ],
                list(
                    map(
                        lambda x: f"{x:.5g}",
                        self.__analyzer.wavelengths[
                            :: int(len(self.__analyzer.wavelengths) / 7)
                        ],
                    )
                ),
            )
            spectrogram_ax.set_title(f"{self.__name} Spectrogram")

            color_bar = plt.colorbar(img, orientation="horizontal")
            color_bar.set_label(f"Power ({self.__power_unit})")

            plt.gcf().set_size_inches(8, 10)

            title = f"{self.__name} Peak Shift with Overlay"
            if self.__ui.autoSaveCheckBox.isChecked():
                plt.savefig(title.replace(" ", "_").lower() + ".png")
            plt.show()

    __signal_work_start = Signal()
    signal_work_done = Signal(bool)

    __signal_fsr_er_q_work_start = Signal()
    signal_fsr_er_q_work_done = Signal(bool)

    def __init__(self):
        super().__init__()
        self.__signal_work_start.connect(self.__slot_work_start)
        self.__signal_fsr_er_q_work_start.connect(self.__slot_fsr_er_q_work_start)

        self.setLayout(QVBoxLayout())
        self.__tab_widget = QTabWidget()
        self.layout().addWidget(self.__tab_widget)

    def plot_initial(
        self,
        analyzer: Analyzer,
        channels: set[int],
        start_stop_step: tuple[int, Optional[int], int],
        time_unit: str,
        wavelength_unit: str,
        power_unit: str,
        r2_threshold: float,
        max_n100dBm_points: int,
    ):
        self.__analyzer = analyzer
        self.__channels = channels
        self.__start_stop_step = start_stop_step
        self.__time_unit = time_unit
        self.__wavelength_unit = wavelength_unit
        self.__power_unit = power_unit
        self.__r2_threshold = r2_threshold
        self.__max_n100dBm_points = max_n100dBm_points

        self.__signal_work_start.emit()
        self.__tab_widget.clear()

    def clear(self):
        self.__tab_widget.clear()

    def save_results(self, path: str):
        all_tabs: list[RaPeakTrackerWidget.__Tab] = [self.__tab_widget.widget(i) for i in range(self.__tab_widget.count())]  # type: ignore

        # save initial path
        temp_dir = os.curdir
        os.chdir(path)

        # save peak shifts
        savemat(
            "peak_shifts.mat",
            {
                (tab.name).replace(" ", "_").lower() + "_peakWL_list": tab.full_trace
                for tab in all_tabs
            }
            | {
                "t_array": self.__analyzer.timestamps[
                    self.__start_stop_step[0] : self.__start_stop_step[
                        1
                    ] : self.__start_stop_step[2]
                ]
            },
        )

        # save all fitted peaks and peak trace indices
        savemat(
            "peaks.mat",
            {
                "channel" + str(k + 1): np.array(v, dtype="object")
                for k, v in self.__all_peaks.items()
            }
            | {
                "t_array": self.__analyzer.timestamps[
                    self.__start_stop_step[0] : self.__start_stop_step[
                        1
                    ] : self.__start_stop_step[2]
                ]
            }
            | {
                "channel"
                + str(tab.power_index + 1)
                + "_peak_trace_indices": np.array(
                    group_peaks(
                        [[p[0] for p in ps] for ps in self.__all_peaks[tab.power_index]],  # type: ignore
                        tab.full_trace,
                    ),
                    dtype="object",
                )
                for tab in all_tabs
            },
        )

        # restore initial path
        os.chdir(temp_dir)

        plt.close("all")
        axes = plt.axes()
        for tab in all_tabs:
            axes.plot(
                self.__analyzer.timestamps[
                    self.__start_stop_step[0] : self.__start_stop_step[
                        1
                    ] : self.__start_stop_step[2]
                ],
                tab.full_trace - tab.full_trace[0],
                label=tab.name,
            )
        axes.set_title("Collated Overlaid Peak Shifts")
        axes.set_xlabel(f"Time ({self.__time_unit})")
        axes.set_ylabel(f"Resonance Peak Shift ({self.__wavelength_unit})")
        plt.gcf().set_size_inches(8, 5)
        axes.axis("auto")
        axes.legend()
        plt.show()
        plt.savefig("Collated Overlaid Peak Shifts.png")

    def __plot_traces(self):
        for c in self.__all_traces.keys():
            tab = self.__Tab(
                c,
                self.__all_traces[c][0],
                self.__all_traces[c][1],
                self.__analyzer,
                self.__start_stop_step,
                self.__time_unit,
                self.__wavelength_unit,
                self.__power_unit,
                self,
            )
            self.__tab_widget.addTab(tab, f"Power{c+1}")

    @Slot()
    def __slot_work_start(self):
        self.__worker = self.__Worker(
            self.__analyzer,
            self.__channels,
            self.__start_stop_step,
            self.__r2_threshold,
            self.__max_n100dBm_points,
        )
        self.__worker.finished.connect(self.__slot_work_done)  # type: ignore
        self.__worker.start()
        self.signal_work_done.emit(False)
        logger.info("Peak Tracking started!")

    @Slot()
    def __slot_work_done(self):
        try:
            self.__all_traces = self.__worker.all_traces
            self.__all_peaks = self.__worker.all_peaks
            self.__plot_traces()
        except Exception as e:
            logger.error(e)
        finally:
            self.__worker.deleteLater()
            self.signal_work_done.emit(True)
            logger.info("Peak Tracking finished!")

    def fsr_er_q(
        self,
        analyzer: Analyzer,
        channels: set[int],
        start_stop_step: tuple[int, Optional[int], int],
        path: str,
    ):
        self.__analyzer = analyzer
        self.__channels = channels
        self.__start_stop_step = start_stop_step
        self.__signal_fsr_er_q_work_start.emit()
        self.__path = path

    @Slot()
    def __slot_fsr_er_q_work_start(self):
        self.__fsr_er_q_worker = self.__FSR_ER_Q_Worker(
            self.__analyzer,
            self.__channels,
            self.__start_stop_step,
            self.__r2_threshold,
            self.__max_n100dBm_points,
        )
        self.__fsr_er_q_worker.finished.connect(self.__slot_fsr_er_q_work_done)  # type: ignore
        self.__fsr_er_q_worker.start()
        self.signal_fsr_er_q_work_done.emit(False)
        logger.info("FSR ER Q analysis started!")

    @Slot()
    def __slot_fsr_er_q_work_done(self):
        temp_dir = os.curdir
        os.chdir(self.__path)

        try:
            fsr_er_q_dict = self.__fsr_er_q_worker.fsr_er_q_dict
            fsr = {k: [np.array(vv[0]) for vv in v] for k, v in fsr_er_q_dict.items()}
            er = {k: [np.array(vv[1]) for vv in v] for k, v in fsr_er_q_dict.items()}
            q = {k: [np.array(vv[2]) for vv in v] for k, v in fsr_er_q_dict.items()}

            savemat(
                "fsr_er_q.mat",
                {
                    f"channel{k+1}_fsr": np.array(v, dtype="object")
                    for k, v in fsr.items()
                }
                | {
                    f"channel{k+1}_er": np.array(v, dtype="object")
                    for k, v in er.items()
                }
                | {f"channel{k+1}_q": np.array(v, dtype="object") for k, v in q.items()}
                | {
                    "t_array": self.__analyzer.timestamps[
                        self.__start_stop_step[0] : self.__start_stop_step[
                            1
                        ] : self.__start_stop_step[2]
                    ]
                },
            )
        except Exception as e:
            logger.error(e)
        finally:
            self.__fsr_er_q_worker.deleteLater()
            self.signal_fsr_er_q_work_done.emit(True)
            os.chdir(temp_dir)
            logger.info("FSR ER Q analysis done!")
