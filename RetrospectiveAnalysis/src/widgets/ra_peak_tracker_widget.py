import logging

from itertools import starmap, cycle


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


class RaPeakTrackerTab(QWidget):
    def __init__(
        self,
        power_index: int,
        traces: list[list[float]],
        fsr: float,
        analyzer: Analyzer,
        parent=None,
    ):
        super().__init__(parent)
        self.ui = Ui_PeakTrackerTabSettingWidget()
        self.ui.setupUi(self)

        self.__name = f"Power {power_index+1}"
        self.__power_index = power_index
        self.__traces = traces
        self.__fsr = fsr
        self.__fsr_multipliers = [0 for x in traces]
        self.__offsets = [0.0 for x in traces]
        self.__timestamps = analyzer.timestamps
        self.__analyzer = analyzer

        self.__figure_widget = RaFigureWidget()
        self.ui.splitter.addWidget(self.__figure_widget)
        self.ui.splitter.setStretchFactor(self.ui.splitter.count() - 1, 1)

        self.ui.doubleSpinBox.valueChanged.connect(self.__slot_update_offsets)  # type: ignore
        self.ui.spinBox.valueChanged.connect(self.__slot_update_offsets)  # type: ignore
        self.ui.comboBox.currentIndexChanged.connect(self.__slot_switch_traces)  # type: ignore

        self.ui.plotPeakOffsetButton.clicked.connect(self.__slot_plot_peak_offset)  # type: ignore
        self.ui.plotOverlayButton.clicked.connect(self.__slot_plot_overlay)  # type: ignore
        self.ui.plotOffsetSpectrogramButton.clicked.connect(self.__slot_plot_offset_spectrogram)  # type: ignore

        self.ui.assayComboBox.currentIndexChanged.connect(parent.slot_update_assay_name)  # type: ignore

        x0 = 0
        for i, trace in enumerate(self.__traces):
            self.ui.comboBox.addItem(
                f"Trace{i+1} (Time {self.__timestamps[x0]:.6g}-{self.__timestamps[x0+len(trace)-1]:.6g})"
            )
            x0 += len(trace)

    def update(self):
        self.__figure_widget.figure.clear()
        ax = self.__figure_widget.figure.subplots()
        ax.set_title(f"{self.__name} Peak Shift")
        ax.set_xlabel("Time (minutes)")
        ax.set_ylabel("Wavelength (nm)")

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
    def assay(self):
        return self.ui.assayComboBox.currentText()

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
        index = self.ui.comboBox.currentIndex()
        self.__fsr_multipliers[index] = self.ui.spinBox.value()
        self.__offsets[index] = self.ui.doubleSpinBox.value()
        self.update()

    @Slot()
    def __slot_switch_traces(self):
        index = self.ui.comboBox.currentIndex()
        self.ui.spinBox.blockSignals(True)
        self.ui.doubleSpinBox.blockSignals(True)
        self.ui.spinBox.setValue(self.__fsr_multipliers[index])
        self.ui.spinBox.setSuffix(f"×{self.__fsr:.6g}")
        self.ui.doubleSpinBox.setValue(self.__offsets[index])
        self.ui.spinBox.blockSignals(False)
        self.ui.doubleSpinBox.blockSignals(False)

    @Slot()
    def __slot_plot_peak_offset(self):
        plt.close("all")
        fig, ax = plt.subplots()

        ys = self.full_trace - self.full_trace[0]

        ax.plot(self.__timestamps[: len(ys)], ys)
        ax.set_xlabel("Time (minutes)")
        ax.set_ylabel("Peak Shift (nm)")
        fig.set_size_inches(8, 5)
        ax.axis("auto")
        title = f"{self.__name} Peak Offset"
        ax.set_title(title)
        if self.ui.autoSaveCheckBox.isChecked():
            plt.savefig(title.replace(" ", "_").lower() + ".png")
        plt.show()

    @Slot()
    def __slot_plot_overlay(self):
        plt.close("all")
        fig, ax = plt.subplots()

        spectrogram = self.__analyzer.get_spectrograms([self.__power_index])[
            self.__power_index
        ]
        ys = self.full_trace
        ys -= min(self.__analyzer.wavelengths)
        ys /= max(self.__analyzer.wavelengths) - min(self.__analyzer.wavelengths)
        ys *= len(self.__analyzer.wavelengths)

        img = ax.imshow(np.flip(spectrogram, 0), cmap="inferno", origin="lower")
        color_bar = fig.colorbar(img, orientation="horizontal")
        color_bar.set_label(f"Power (dBm)")

        ax.plot(ys)
        ax.set_xlabel("Time (minutes)")
        ax.set_xticks([0, len(ys) - 1], [0, f"{self.__analyzer.timestamps[-1]:.5g}"])
        ax.set_ylabel("Wavelength (nm)")
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
        if self.ui.autoSaveCheckBox.isChecked():
            plt.savefig(title.replace(" ", "_").lower() + ".png")
        plt.show()

    @Slot()
    def __slot_plot_offset_spectrogram(self):
        plt.close("all")

        trace_ax = plt.subplot(2, 1, 1)
        ys = self.full_trace
        ys -= ys[0]
        trace_ax.plot(self.__timestamps[: len(ys)], ys)
        trace_ax.set_xlabel("Time (minutes)")
        trace_ax.set_ylabel("Wavelength (nm)")
        trace_ax.set_title(f"{self.__name} Peak Offset")

        spectrogram_ax = plt.subplot(2, 1, 2)
        spectrogram = self.__analyzer.get_spectrograms([self.__power_index])[
            self.__power_index
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
        spectrogram_ax.set_xlabel("Time (min)")
        spectrogram_ax.set_xticks(
            [0, len(ys) - 1], [0, f"{self.__analyzer.timestamps[-1]:.5g}"]
        )
        spectrogram_ax.set_ylabel("Wavelength (nm)")
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
        color_bar.set_label(f"Power (dBm)")

        plt.gcf().set_size_inches(8, 10)

        title = f"{self.__name} Peak Shift with Overlay"
        if self.ui.autoSaveCheckBox.isChecked():
            plt.savefig(title.replace(" ", "_").lower() + ".png")
        plt.show()


class RaPeakTrackerWidgetWorker(QThread):
    def __init__(
        self,
        analyzer: Analyzer,
        channels: list[int],
        prominence: float,
    ):
        super().__init__()
        self.__analyzer = analyzer
        self.__channels = channels
        self.__prominence = prominence

    def run(self):
        self.__all_traces, self.__all_peaks = self.__analyzer.analyze(
            self.__channels,
            self.__prominence,
        )

    @property
    def all_traces(self):
        return self.__all_traces

    @property
    def all_peaks(self):
        return self.__all_peaks


class RaPeakTrackerWidget(QWidget):
    __signal_work_start = Signal()
    signal_work_done = Signal(bool)

    def __init__(self):
        super().__init__()
        self.__signal_work_start.connect(self.__slot_work_start)

        self.setLayout(QVBoxLayout())
        self.__tab_widget = QTabWidget()
        self.layout().addWidget(self.__tab_widget)

        self.__assay_name_hint: set[str] = set()

    def plot_initial(
        self,
        analyzer: Analyzer,
        channels: list[int],
        prominence: float,
    ):
        self.__analyzer = analyzer
        self.__channels = channels
        self.__prominence = prominence
        self.__signal_work_start.emit()
        self.__tab_widget.clear()

    def clear(self):
        self.__tab_widget.clear()

    def save_results(self):
        all_tabs: list[RaPeakTrackerTab] = [self.__tab_widget.widget(i) for i in range(self.__tab_widget.count())]  # type: ignore

        # save peak shifts
        savemat(
            f"peak_shifts.mat",
            {
                # (tab.name + "_" + tab.assay)
                (tab.name).replace(" ", "_").lower() + "_peakWL_list": tab.full_trace
                for tab in all_tabs
            }
            | {"t_array": self.__analyzer.timestamps},
        )

        # save all fitted peaks
        savemat(
            f"peaks.mat",
            {"power" + str(k + 1): v for k, v in self.__all_peaks.items()}
            | {"t_array": self.__analyzer.timestamps},
        )

        mpl_default_colors: cycle[tuple[float]] = cycle(
            map(
                lambda x: tuple(
                    int(x.lstrip("#")[i : i + 2], 16) / 255
                    for i in (0, 2, 4)  # convert hex to rgb tuple
                ),
                plt.rcParams["axes.prop_cycle"].by_key()["color"],  # type: ignore
            )
        )

        plt.close("all")
        axes = plt.axes()
        assay_dict: dict[str, list[int]] = {}
        for i, tab in enumerate(all_tabs):
            assay_dict[tab.assay] = assay_dict.get(tab.assay, []) + [i]
        for k, v in assay_dict.items():
            lines = []
            for index in v:
                tab = all_tabs[index]
                lines.append(tab.full_trace - tab.full_trace[0])

            timestamps = self.__analyzer.timestamps

            line_collection = LineCollection(
                list(map(lambda x: list(zip(timestamps, x)), lines)),
                color=next(mpl_default_colors),  # type: ignore
                label=k,  # type: ignore
            )
            axes.add_collection(
                line_collection,
            )
        axes.set_title("Collated Overlaid Peak Shifts")
        axes.set_xlabel("Time (minutes)")
        axes.set_ylabel("Resonance Peak Shift (nm)")
        plt.gcf().set_size_inches(8, 5)
        axes.axis("auto")
        axes.legend()
        plt.show()

    def __plot_traces(self):
        for c in self.__all_traces.keys():
            tab = RaPeakTrackerTab(
                c,
                self.__all_traces[c][0],
                self.__all_traces[c][1],
                self.__analyzer,
                self,
            )
            self.__tab_widget.addTab(tab, f"Power{c+1}")
            tab.update()

    @Slot()
    def slot_update_assay_name(self):
        self.__assay_name_hint.clear()
        all_tabs: list[RaPeakTrackerTab] = [self.__tab_widget.widget(i) for i in range(self.__tab_widget.count())]  # type: ignore
        for tab in all_tabs:
            self.__assay_name_hint.add(tab.assay)
        for tab in all_tabs:
            tab.ui.assayComboBox.setCompleter(QCompleter(list(self.__assay_name_hint)))
            item_texts = [
                tab.ui.assayComboBox.itemText(i)
                for i in range(tab.ui.assayComboBox.count())
            ]
            tab.ui.assayComboBox.addItems(
                [s for s in self.__assay_name_hint if s != "" and s not in item_texts]
            )

    @Slot()
    def __slot_work_start(self):
        self.__worker = RaPeakTrackerWidgetWorker(
            self.__analyzer,
            self.__channels,
            self.__prominence,
        )
        self.__worker.finished.connect(self.__slot_work_done)  # type: ignore
        self.__worker.start()
        self.signal_work_done.emit(False)
        logger.info("Peak Tracking started!")

    @Slot()
    def __slot_work_done(self):
        self.__worker.finished.disconnect(self.__slot_work_done)  # type: ignore
        self.__all_traces = self.__worker.all_traces
        self.__all_peaks = self.__worker.all_peaks
        self.__worker.deleteLater()
        self.__plot_traces()
        self.signal_work_done.emit(True)
        logger.info("Peak Tracking finished!")
