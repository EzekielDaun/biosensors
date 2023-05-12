import logging
import multiprocessing as mp
import os
import re
import sys
from collections.abc import Callable
from functools import reduce
from itertools import cycle, islice, repeat
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import toml
from numpy.typing import NDArray
from pyqtgraph import PlotWidget, ScatterPlotItem
from PySide6.QtCore import QDir, Qt, QThread, Signal, Slot
from PySide6.QtGui import QTextCursor, QTransform
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QVBoxLayout,
)
from scipy.io import savemat

from ..core.active_tools import (
    RampUpSweepCSVReader,
    generate_wavelength,
    thermal_simulation,
)
from ..core.lib import (
    get_lorentzian_peaks,
    group_peaks,
    peaks_to_traces,
)
from ..uic.ra_main_window_active import Ui_RaMainWindowActive

logger = logging.getLogger(__name__)


def sweep_to_wavelength_fsr(
    power_time, tau: float, wavelength_range: tuple[float, float], frequency: float
):
    power, time = power_time
    temp_reference = thermal_simulation(frequency, 50, 1000, tau)
    wavelength, power = generate_wavelength(power, temp_reference, wavelength_range)
    peaks, fsr, er, q = get_lorentzian_peaks(power, wavelength)
    if len(fsr) > 1:
        return [[peaks[i][0], fsr[i]] for i in range(len(fsr))]
    else:
        return []


def sweep_to_spectrum(power_time, tau: float, wavelength_interpolate, frequency: float):
    power, time = power_time
    temp_reference = thermal_simulation(frequency, 50, 1000, tau)
    wavelength, power = generate_wavelength(
        power,
        temp_reference,
        (min(wavelength_interpolate), max(wavelength_interpolate)),
    )
    return np.interp(wavelength_interpolate, wavelength, power), time


class RaPlotCurveItem(pg.PlotCurveItem):
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


class RaMainWindow(QMainWindow):
    class __Worker(QThread):
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

    __signal_write = Signal(str)

    def __init__(self):
        super().__init__()
        self.__ui = Ui_RaMainWindowActive()
        self.__ui.setupUi(self)

        self.__ui.rampSettingDataSelectPushButton.clicked.connect(self.slot_ramp_setting_data_path_browse)  # type: ignore
        self.__ui.peakTrackingOutputPathPushButton.clicked.connect(self.slot_peak_tracking_output_path_browse)  # type: ignore

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # Shared Spectrogram
        self.__spectrogram: Optional[NDArray[np.float64]] = None

        # Ramp setting FSR plot
        self.__ramp_setting_FSR_plot_widget = PlotWidget()
        self.__ui.rampSettingFSRPlotWidget.setLayout(QVBoxLayout())
        self.__ui.rampSettingFSRPlotWidget.layout().addWidget(
            self.__ramp_setting_FSR_plot_widget
        )
        self.__ramp_setting_FSR_plot_widget.getPlotItem().showGrid(x=True, y=True)  # type: ignore
        self.__ramp_setting_FSR_plot_widget.getPlotItem().getAxis("left").setLabel(text="FSR", units="m")  # type: ignore
        self.__ramp_setting_FSR_plot_widget.getPlotItem().getAxis("bottom").setLabel(text="Wavelength", units="m")  # type: ignore

        self.__ramp_setting_FSR_scatter_plot_item = ScatterPlotItem()
        self.__ramp_setting_FSR_plot_widget.addItem(
            self.__ramp_setting_FSR_scatter_plot_item
        )

        self.__ramp_setting_parameter_dict = {}
        # self.__ramp_setting_parameter_dict["R_heater"] = 40
        # self.__ramp_setting_parameter_dict["voltage_exponent"] = 2
        # self.__ramp_setting_parameter_dict["V_min"] = 0
        # self.__ramp_setting_parameter_dict["V_max"] = 3
        # self.__ramp_setting_parameter_dict["WL_Ip1"] = 0.0016
        # self.__ramp_setting_parameter_dict["WL_Ip2"] = 2.3236e-5
        # self.__ramp_setting_parameter_dict["WL_p1"] = -2.55
        # self.__ramp_setting_parameter_dict["Temp_p0"] = 1.309158353754940e3
        # self.__ramp_setting_parameter_dict["Temp_p1"] = 0.069458992094887
        # self.__ramp_setting_parameter_dict["laser_current"] = 20e-3
        # self.__ramp_setting_parameter_dict["laser_temperature"] = 12

        # Peak Tracker Spectrogram Image View
        self.__peak_tracking_spectrogram_plot_item = pg.PlotItem()
        self.__peak_tracking_spectrogram_plot_item.setLabel(
            axis="bottom", text="Sweep Number"
        )
        self.__peak_tracking_spectrogram_plot_item.getAxis("left").setLabel(
            text="Wavelength", units="m"
        )

        self.__peak_tracking_spectrogram_image_view = pg.ImageView(view=self.__peak_tracking_spectrogram_plot_item)  # type: ignore
        self.__peak_tracking_spectrogram_image_view.ui.roiBtn.hide()
        self.__peak_tracking_spectrogram_image_view.ui.menuBtn.hide()
        self.__peak_tracking_spectrogram_image_view.getView().invertY(False)
        self.__peak_tracking_spectrogram_image_view.getView().setAspectLocked(False)
        self.__peak_tracking_spectrogram_image_view.setColorMap(
            pg.colormap.get("inferno")
        )

        self.__ui.peakTrackerWidget.setLayout(QVBoxLayout())
        self.__ui.peakTrackerWidget.layout().addWidget(
            self.__peak_tracking_spectrogram_image_view
        )

        # Redirect stdout and stderr to log panel
        self.__signal_write.connect(self.slot_log_write)
        sys.stdout = self
        sys.stderr = self

    # stdout redirection requirement
    def write(self, m):
        self.__signal_write.emit(m)

    # stdout redirection requirement
    def flush(self):
        pass

    @Slot()
    def slot_log_write(self, text):
        self.__ui.textBrowser.moveCursor(QTextCursor.End)  # type: ignore
        self.__ui.textBrowser.insertPlainText(text)
        self.__ui.textBrowser.ensureCursorVisible()

    # Slots
    # Ramp setting slots
    @Slot()
    def slot_ramp_setting_data_path_browse(self):
        if path := QFileDialog.getExistingDirectory(
            self, "Select a folder", QDir.currentPath()
        ):
            self.__ui.rampSettingDataPathComboBox.addItem(path)
            self.__ui.rampSettingDataPathComboBox.setCurrentText(path)
            if os.path.exists(os.path.join(path, "config.toml")):
                logger.info("Config file found")
                config_dict = toml.load(os.path.join(path, "config.toml"))
                for k, v in config_dict.items():
                    # update UI parameters
                    if k == "regex":
                        self.__ui.rampSettingRegExLineEdit.setText(v)
                    elif k == "ramp_type":
                        self.__ui.rampSettingRampTypeComboBox.setCurrentText(v)
                    elif k == "ramp_frequency":
                        self.__ui.rampSettingRampFrequencyDoubleSpinBox.setValue(v)
                    elif k == "wavelength_min":
                        self.__ui.rampSettingWavelengthMinDoubleSpinBox.setValue(v)
                    elif k == "wavelength_max":
                        self.__ui.rampSettingWavelengthMaxDoubleSpinBox.setValue(v)
                    elif k == "time_constant":
                        self.__ui.rampSettingTimeConstantDoubleSpinBox.setValue(v)
                    elif k in self.__ramp_setting_parameter_dict:
                        # update other parameters not in UI
                        self.__ramp_setting_parameter_dict[k] = v
                    else:
                        logger.info(f"Unknown key {k}, omit")
                for k, v in self.__ramp_setting_parameter_dict.items():
                    if k not in config_dict.keys():
                        logger.warning(f"Missing {k}. Use default value {k} = {v}")
            else:
                logger.warning(
                    f"No configuration file. Use default parameters.\n{self.__ramp_setting_parameter_dict}"
                )
        else:  # cancel
            pass

    def slot_ramp_setting_update(self):
        path = os.path.expanduser(self.__ui.rampSettingDataPathComboBox.currentText())
        pattern = re.compile(self.__ui.rampSettingRegExLineEdit.text())
        reader = RampUpSweepCSVReader(
            path, pattern, self.__ui.rampSettingRampFrequencyDoubleSpinBox.value()
        )

        start, stop, step = (
            self.__ui.rampSettingStartSpinBox.value(),
            self.__ui.rampSettingStopSpinBox.value(),
            self.__ui.rampSettingStepSpinBox.value(),
        )

        tau = self.__ui.rampSettingTimeConstantDoubleSpinBox.value()
        wavelength_range = (
            self.__ui.rampSettingWavelengthMinDoubleSpinBox.value(),
            self.__ui.rampSettingWavelengthMaxDoubleSpinBox.value(),
        )
        frequency = self.__ui.rampSettingRampFrequencyDoubleSpinBox.value()

        def get_fsr(reader: RampUpSweepCSVReader, start, stop, step):
            with mp.Pool() as pool:
                return reduce(
                    lambda acc, x: acc + x,
                    pool.starmap(
                        sweep_to_wavelength_fsr,
                        zip(
                            islice(reader, start, stop, step),
                            repeat(tau),
                            repeat(wavelength_range),
                            repeat(frequency),
                        ),
                    ),
                    [],
                )

        self.__ui.rampSettingUpdatePushButton.clearFocus()
        self.__ui.rampSettingUpdatePushButton.setEnabled(False)

        self.ramp_setting_worker = self.__Worker(get_fsr, reader, start, stop, step)  # type: ignore
        self.ramp_setting_worker.finished.connect(self.slot_ramp_setting_update_plot)
        self.ramp_setting_worker.start()

    @Slot()
    def slot_ramp_setting_update_plot(self):
        scatter_data = np.array(self.ramp_setting_worker.result) * 1e-9  # SI units
        self.ramp_setting_worker.deleteLater()

        self.__ramp_setting_FSR_scatter_plot_item.setData(
            scatter_data[:, 0], scatter_data[:, 1]
        )
        self.__ramp_setting_FSR_plot_widget.autoRange()

        self.__ui.rampSettingUpdatePushButton.setEnabled(True)

        # save parameters as toml
        toml_dict = {}
        toml_dict.update(self.__ramp_setting_parameter_dict)
        toml_dict["regex"] = self.__ui.rampSettingRegExLineEdit.text()
        toml_dict["ramp_type"] = self.__ui.rampSettingRampTypeComboBox.currentText()
        toml_dict[
            "ramp_frequency"
        ] = self.__ui.rampSettingRampFrequencyDoubleSpinBox.value()
        toml_dict[
            "wavelength_min"
        ] = self.__ui.rampSettingWavelengthMinDoubleSpinBox.value()
        toml_dict[
            "wavelength_max"
        ] = self.__ui.rampSettingWavelengthMaxDoubleSpinBox.value()
        toml_dict[
            "time_constant"
        ] = self.__ui.rampSettingTimeConstantDoubleSpinBox.value()
        with open(
            os.path.join(
                os.path.expanduser(self.__ui.rampSettingDataPathComboBox.currentText()),
                "config.toml",
            ),
            "w",
            encoding="utf-8",
        ) as f:
            toml.dump(toml_dict, f)

    # Peak tracking slots
    @Slot()
    def slot_peak_tracking_output_path_browse(self):
        path = QFileDialog.getExistingDirectory(
            dir=Path(
                self.__ui.rampSettingDataPathComboBox.currentText()
            ).parent.__str__()
        )
        if path:
            self.__ui.peakTrackingOutputPathComboBox.setCurrentText(path)
            self.__ui.peakTrackingOutputPathComboBox.addItem(path)
        else:
            pass

    def slot_peak_tracking_spectrogram(self):
        # remove all curve items except the image item and roi item
        temp = []
        for item in self.__peak_tracking_spectrogram_plot_item.items:
            if (
                item is self.__peak_tracking_spectrogram_image_view.imageItem
                or item is self.__peak_tracking_spectrogram_image_view.roi
            ):
                temp.append(item)
        self.__peak_tracking_spectrogram_plot_item.clear()
        for item in temp:
            self.__peak_tracking_spectrogram_plot_item.addItem(item)

        # clear image
        self.__peak_tracking_spectrogram_image_view.clear()

        path = os.path.expanduser(self.__ui.rampSettingDataPathComboBox.currentText())
        pattern = re.compile(self.__ui.rampSettingRegExLineEdit.text())
        reader = RampUpSweepCSVReader(
            path, pattern, self.__ui.rampSettingRampFrequencyDoubleSpinBox.value()
        )

        tau = self.__ui.rampSettingTimeConstantDoubleSpinBox.value()

        frequency = self.__ui.rampSettingRampFrequencyDoubleSpinBox.value()

        sweep_start, sweep_stop, sweep_step = (
            self.__ui.peakTrackingSweepStartSpinBox.value(),
            self.__ui.peakTrackingSweepStopSpinBox.value(),
            self.__ui.peakTrackingSweepStepSpinBox.value(),
        )

        self.__wavelength_interpolate = np.linspace(
            self.__ui.rampSettingWavelengthMinDoubleSpinBox.value(),
            self.__ui.rampSettingWavelengthMaxDoubleSpinBox.value(),
            self.__ui.peakTrackingWavelengthSampleSpinBox.value(),
        )

        def get_spectrogram(reader: RampUpSweepCSVReader, start, stop, step):
            with mp.Pool() as pool:
                spectrogram, time_stamp = reduce(
                    lambda acc, x: (acc[0] + [x[0]], acc[1] + [x[1]]),
                    pool.starmap(
                        sweep_to_spectrum,
                        zip(
                            islice(reader, start, stop, step),
                            repeat(tau),
                            repeat(self.__wavelength_interpolate),
                            repeat(frequency),
                        ),
                    ),
                    ([], []),
                )
                return np.array(spectrogram), np.array(time_stamp)

        self.__ui.peakTrackingSpectrogramButton.clearFocus()
        self.__ui.peakTrackingSpectrogramButton.setEnabled(False)
        self.__ui.peakTrackingTrackPeakButton.setEnabled(False)
        self.__ui.peakTrackingSaveResultsButton.setEnabled(False)
        self.spectrogram_worker = self.__Worker(get_spectrogram, reader, sweep_start, sweep_stop, sweep_step)  # type: ignore
        self.spectrogram_worker.finished.connect(
            self.slot_peak_tracking_spectrogram_update_plot
        )
        self.spectrogram_worker.start()

    @Slot()
    def slot_peak_tracking_spectrogram_update_plot(self):
        self.__spectrogram, self.__time_stamp = self.spectrogram_worker.result

        self.__peak_tracking_spectrogram_image_view.setImage(self.__spectrogram)
        tr = QTransform()
        tr.translate(0, min(self.__wavelength_interpolate) / 1e9)
        tr.scale(
            1,
            (max(self.__wavelength_interpolate) - min(self.__wavelength_interpolate))
            * 1e-9
            / len(self.__wavelength_interpolate),
        )
        self.__peak_tracking_spectrogram_image_view.imageItem.setTransform(tr)
        self.__peak_tracking_spectrogram_image_view.getView().autoRange()

        self.spectrogram_worker.deleteLater()
        self.__ui.peakTrackingSpectrogramButton.setEnabled(True)
        self.__ui.peakTrackingTrackPeakButton.setEnabled(True)

    def slot_peak_tracking_track_peak(self):
        if self.__spectrogram is not None:
            self.__ui.peakTrackingTrackPeakButton.clearFocus()
            self.__ui.peakTrackingTrackPeakButton.setEnabled(False)

            def get_peaks_fsr_er_q_traces(powers: NDArray[np.float64]):
                with mp.Pool() as pool:
                    peaks, fsr, er, q = reduce(
                        lambda acc, x: [
                            acc[0] + [x[0]],
                            acc[1] + [x[1]],
                            acc[2] + [x[2]],
                            acc[3] + [x[3]],
                        ],
                        pool.starmap(get_lorentzian_peaks, zip(powers, repeat(self.__wavelength_interpolate))),  # type: ignore
                        [[], [], [], []],
                    )

                    return peaks_to_traces(peaks), peaks, fsr, er, q

            self.peak_tracking_worker = self.__Worker(get_peaks_fsr_er_q_traces, self.__spectrogram)  # type: ignore
            self.peak_tracking_worker.finished.connect(
                self.slot_peak_tracking_track_peak_update_plot
            )
            self.peak_tracking_worker.start()

    @Slot()
    def slot_peak_tracking_track_peak_update_plot(self):
        (
            (traces, fsr),
            self.__result_peaks,
            self.__result_fsr,
            self.__result_er,
            self.__result_q,
        ) = self.peak_tracking_worker.result

        color_palette = cycle(["light green", "grey"])

        x0 = 0
        for trace in traces:
            curve_item = RaPlotCurveItem(
                fsr=fsr / 1e9,
                x=np.arange(x0, x0 + len(trace), 1),
                y=np.array(trace) / 1e9,
                pen={"color": next(color_palette), "width": 5, "cosmetic": True},
            )
            x0 += len(trace)
            self.__peak_tracking_spectrogram_plot_item.addItem(curve_item)

        self.peak_tracking_worker.deleteLater()
        self.__ui.peakTrackingTrackPeakButton.setEnabled(True)
        self.__ui.peakTrackingSaveResultsButton.setEnabled(True)

    def slot_peak_tracking_save_results(self):
        trace_items = [
            np.array(i.getData())
            for i in self.__peak_tracking_spectrogram_plot_item.items
            if isinstance(i, RaPlotCurveItem)
        ]

        sweep_index, peak_shift = np.hstack(trace_items)
        peak_shift *= 1e9

        peak_wavelengths = [
            np.array([x[0] for x in sweep]) for sweep in self.__result_peaks
        ]
        traces = np.array(group_peaks(peak_wavelengths, peak_shift), dtype="object")
        savemat(
            os.path.join(
                self.__ui.peakTrackingOutputPathComboBox.currentText(), "result.mat"
            ),
            {
                "lorentzian_peaks": np.array(self.__result_peaks, dtype="object"),
                "fsr": np.array(self.__result_fsr, dtype="object"),
                "er": np.array(self.__result_er, dtype="object"),
                "q": np.array(self.__result_q, dtype="object"),
                "sweep": sweep_index,
                "peak_shift": peak_shift,
                "traces": traces,
            },
        )

        plt.plot(sweep_index, peak_shift)
        plt.show()
