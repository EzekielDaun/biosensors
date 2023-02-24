import logging

from itertools import starmap, cycle
import os

from typing import Optional

import numpy as np

from scipy.io import savemat

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


from PySide6.QtCore import QThread, Slot, Signal
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QCompleter

from .ra_figure_widget import RaFigureWidget
from ..uic.ra_peak_tracker_tab_setting_widget import Ui_PeakTrackerTabSettingWidget
from ..core.retrospective_analysis import RetrospectiveAnalyzer as Analyzer

logger = logging.getLogger(__name__)


class RaPeakTrackerWidget(QWidget):
    class __Worker(QThread):
        def __init__(
            self,
            analyzer: Analyzer,
            channels: list[int],
            start_stop_step: tuple[int, Optional[int], int],
        ):
            super().__init__()
            self.__analyzer = analyzer
            self.__channels = channels
            self.__start_stop_step = start_stop_step

        def run(self):
            self.__all_traces, self.__all_peaks = self.__analyzer.analyze(
                self.__channels,
                self.__start_stop_step,
                [1, 1, 1, 1, 1],
            )

        @property
        def all_traces(self):
            return self.__all_traces

        @property
        def all_peaks(self):
            return self.__all_peaks

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
            self.__fsr_multipliers = [0 for x in traces]
            self.__offsets = [0.0 for x in traces]
            self.__timestamps = analyzer.timestamps[
                start_stop_step[0] : start_stop_step[1] : start_stop_step[2]
            ]
            self.__start_stop_step = start_stop_step
            self.__analyzer = analyzer
            self.__time_unit = time_unit
            self.__power_unit = power_unit
            self.__wavelength_unit = wavelength_unit

            self.__figure_widget = RaFigureWidget()
            self.__ui.splitter.addWidget(self.__figure_widget)
            self.__ui.splitter.setStretchFactor(self.__ui.splitter.count() - 1, 1)

            self.__ui.doubleSpinBox.valueChanged.connect(self.__slot_update_offsets)  # type: ignore
            self.__ui.spinBox.valueChanged.connect(self.__slot_update_offsets)  # type: ignore
            self.__ui.comboBox.currentIndexChanged.connect(self.__slot_switch_traces)  # type: ignore

            self.__ui.plotPeakOffsetButton.clicked.connect(self.__slot_plot_peak_offset)  # type: ignore
            self.__ui.plotOverlayButton.clicked.connect(self.__slot_plot_overlay)  # type: ignore
            self.__ui.plotOffsetSpectrogramButton.clicked.connect(self.__slot_plot_offset_spectrogram)  # type: ignore

            x0 = 0
            for i, trace in enumerate(self.__traces):
                self.__ui.comboBox.addItem(
                    f"Trace{i+1} (Time {self.__timestamps[x0]:.6g}-{self.__timestamps[x0+len(trace)-1]:.6g})"
                )
                x0 += len(trace)

        def update(self):
            self.__figure_widget.figure.clear()
            ax = self.__figure_widget.figure.subplots(1, 1)
            ax.set_title(f"{self.__name} Peak Shift")
            ax.set_xlabel(f"Time ({self.__time_unit})")
            ax.set_ylabel(f"Wavelength ({self.__wavelength_unit})")

            x0 = 0
            for i, trace in enumerate(self.__traces):
                ax.plot(
                    self.__timestamps[x0 : x0 + len(trace)],
                    np.array(trace)
                    + self.__fsr * self.__fsr_multipliers[i]
                    + self.__offsets[i],
                )
                x0 += len(trace)

            self.__figure_widget.figure_canvas.draw()

        @property
        def name(self):
            return self.__name

        @property
        def full_trace(self):
            return np.concatenate(
                tuple(
                    starmap(
                        lambda i, x: np.array(x)
                        + self.__fsr * self.__fsr_multipliers[i]
                        + self.__offsets[i],
                        enumerate(self.__traces),
                    )
                )
            )

        @Slot()
        def __slot_update_offsets(self):
            index = self.__ui.comboBox.currentIndex()
            self.__fsr_multipliers[index] = self.__ui.spinBox.value()
            self.__offsets[index] = self.__ui.doubleSpinBox.value()
            self.update()

        @Slot()
        def __slot_switch_traces(self):
            index = self.__ui.comboBox.currentIndex()
            self.__ui.spinBox.blockSignals(True)
            self.__ui.doubleSpinBox.blockSignals(True)
            self.__ui.spinBox.setValue(self.__fsr_multipliers[index])
            self.__ui.spinBox.setSuffix(f"×{self.__fsr:.6g}")
            self.__ui.doubleSpinBox.setValue(self.__offsets[index])
            self.__ui.spinBox.blockSignals(False)
            self.__ui.doubleSpinBox.blockSignals(False)

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

            spectrogram = self.__analyzer.get_spectrograms([self.__power_index])[
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
            spectrogram = self.__analyzer.get_spectrograms([self.__power_index])[
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

    def __init__(self):
        super().__init__()
        self.__signal_work_start.connect(self.__slot_work_start)

        self.setLayout(QVBoxLayout())
        self.__tab_widget = QTabWidget()
        self.layout().addWidget(self.__tab_widget)

        self.__power_name_hint: set[str] = set()

    def plot_initial(
        self,
        analyzer: Analyzer,
        channels: list[int],
        start_stop_step: tuple[int, Optional[int], int],
        time_unit: str,
        wavelength_unit: str,
        power_unit: str,
    ):
        self.__analyzer = analyzer
        self.__channels = channels
        self.__start_stop_step = start_stop_step
        self.__time_unit = time_unit
        self.__wavelength_unit = wavelength_unit
        self.__power_unit = power_unit
        self.__signal_work_start.emit()
        self.__tab_widget.clear()

    def clear(self):
        self.__tab_widget.clear()

    def save_results(self, path: str):
        all_tabs: list[RaPeakTrackerWidget.__Tab] = [self.__tab_widget.widget(i) for i in range(self.__tab_widget.count())]  # type: ignore

        temp_dir = os.curdir
        os.chdir(path)
        # save peak shifts
        savemat(
            f"peak_shifts.mat",
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

        # save all fitted peaks
        savemat(
            f"peaks.mat",
            {
                "power" + str(k + 1): np.array(v, dtype="object")
                for k, v in self.__all_peaks.items()
            }
            | {
                "t_array": self.__analyzer.timestamps[
                    self.__start_stop_step[0] : self.__start_stop_step[
                        1
                    ] : self.__start_stop_step[2]
                ]
            },
        )
        with open("WhatsThis.txt", "w") as f:
            f.write(
                r"""RA_results
"peak_shifts.mat":
    t_array [1D array]: time stamps
    power_*_peakWL_list [1D array]: tracked peak wavelengths for channel * (offset included)
“peaks.mat”:
    t_array [1D array]: time stamps
    power* [cell array]: all the fitted peaks for channel * (based on unchanged raw data). The number of peaks in each sweep may vary.
            The peak is stored by a 5-element vector [x0,y0,I,gamma,a], representing a sloped Lorentzian function:
                y = y0 + ((I * (gamma / 2) ** 2) / ((gamma / 2) ** 2 + (x - x0) ** 2)) + a * (x - x0)
            where
                [x0] is the peak wavelength
                [y0] is approximately the baseline
                [I] is the peak intensity (negative for absorption peaks)
                [gamma] is the peak width at half height
                [a] is the baseline slope
"""
            )
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
            tab.update()

    @Slot()
    def __slot_work_start(self):
        self.__worker = self.__Worker(
            self.__analyzer, self.__channels, self.__start_stop_step
        )
        self.__worker.finished.connect(self.__slot_work_done)  # type: ignore
        self.__worker.start()
        self.signal_work_done.emit(False)
        logger.info("Peak Tracking started!")

    @Slot()
    def __slot_work_done(self):
        self.__worker.finished.disconnect(self.__slot_work_done)  # type: ignore
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
