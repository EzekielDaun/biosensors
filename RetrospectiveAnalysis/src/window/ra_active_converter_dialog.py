import os
import re
from collections.abc import Callable
from functools import reduce
from itertools import cycle, islice, repeat, starmap
from logging import getLogger
from multiprocessing import Pool
from typing import Any, Optional

import numpy as np
import pyqtgraph as pg
from numpy.typing import NDArray
from pyqtgraph import (
    GraphicsLayoutWidget,
    ImageView,
    PlotItem,
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from scipy.io import savemat
from scipy.signal import impulse2, lsim, sawtooth, step

from ..core.active_tools import (
    ConverterConfig,
    CSVData,
    RampUpSweepCSVReader2,
)
from ..core.lib import get_lorentzian_peaks
from ..uic.active.ra_active_converter_dialog import Ui_RaActiveConverterDialog
from ..widgets.active.ra_conversion_tabs import (
    ConversionRCTFTab,
    ConversionTabBase,
    ConversionZPGTFTab,
)
from ..widgets.active.ra_fsr_tab_widget import (
    RaActiveConverterFSRTabWidget,
)
from ..widgets.active.ra_regulation_tabs import (
    RegulationPhaseShifterTab,
    RegulationPolynomialTab,
    RegulationTabBase,
)

logger = getLogger(__name__)

CONFIG_CSV_DEFAULT_NAME = "ra_config.csv"
OUTPUT_SUBDIR_DEFAULT_NAME = "passive"


# internal multiprocessing functions
def _interpolate_2d_spectrogram_data(data_2d: NDArray, interp_len: int) -> NDArray:
    return np.array(
        [
            np.interp(np.linspace(0, 1, interp_len), np.linspace(0, 1, len(x)), x)
            for x in data_2d
        ]
    )


def _sweep_2d_data_to_wl_fsr(data: NDArray, ref: NDArray, polarity: int):
    ret: list[list[tuple[float, float]]] = [[] for i in range(len(data))]
    for i, channel in enumerate(data):
        ref_interp = np.interp(
            np.linspace(0, 1, len(channel)),
            np.linspace(0, 1, len(ref)),
            ref,
        )

        index = np.argmin(ref_interp * polarity)
        power = channel[index:]
        wavelength = ref_interp[index:]

        indices = np.argsort(wavelength)
        wavelength = wavelength[indices]
        power = power[indices]

        peaks, fsr, er, q = get_lorentzian_peaks(power, wavelength)

        if len(fsr) > 0:
            ret[i] += list(zip(peaks[:, 0], fsr))  # type: ignore
        else:
            pass

    return ret


def _sweep_2d_data_to_passive_format(
    data: NDArray, ref: NDArray, polarity: int, interp_len: int
):
    wavelength_interp = np.linspace(np.min(ref), np.max(ref), interp_len)
    power_2d = [[] for i in range(data.shape[0])]
    for i, channel in enumerate(data):
        ref_interp = np.interp(
            np.linspace(0, 1, len(channel)),
            np.linspace(0, 1, len(ref)),
            ref,
        )

        index = np.argmin(ref_interp * polarity)
        power = channel[index:]
        wavelength = ref_interp[index:]

        indices = np.argsort(wavelength)
        wavelength = wavelength[indices]
        power = power[indices]

        power_interp = np.interp(wavelength_interp, wavelength, power)

        power_2d[i] = power_interp

    ret: dict[str, NDArray] = {
        "power": np.array(power_2d).T,
        "wavelength": 1e-9 * wavelength_interp,
    }
    return ret


class RaActiveConverterDialog(QDialog):
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

    def __init__(self, folder_path: str, parent: Optional[QWidget], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.__ui = Ui_RaActiveConverterDialog()
        self.__ui.setupUi(self)

        self.__folder_path = folder_path
        self.__csv_reader: RampUpSweepCSVReader2 = None  # type: ignore

        # sweep raw preview
        self.__sweep_raw_preview_widget = GraphicsLayoutWidget()
        self.__ui.rawPreviewPlotSpaceholderWidget.setLayout(QHBoxLayout())
        self.__ui.rawPreviewPlotSpaceholderWidget.layout().addWidget(
            self.__sweep_raw_preview_widget
        )
        self.__sweep_raw_preview_widget_ramp_plot = (
            self.__sweep_raw_preview_widget.addPlot(row=1, col=0)
        )
        self.__sweep_raw_preview_widget_data_plot = (
            self.__sweep_raw_preview_widget.addPlot(row=0, col=0)
        )
        self.__sweep_raw_preview_widget_data_plot.addLegend()
        self.__sweep_raw_preview_widget_data_plot.setXLink(
            self.__sweep_raw_preview_widget_ramp_plot.getViewBox()
        )

        self.__ui.rawLoadPushButton.clicked.connect(
            self.slot_on_sweep_raw_preview_setting_load
        )
        self.__ui.rawPreviewFileComboBox.currentIndexChanged.connect(
            self.slot_on_sweep_raw_preview_file_changed
        )

        # spectrogram raw preview
        self.__ui.rawSpectrogramPlotPushButton.clicked.connect(
            self.slot_on_plot_spectrogram_clicked
        )

        plot_item = PlotItem()
        plot_item.setLabel(axis="bottom", text="Sweep Number")
        plot_item.setLabel(axis="left", text="Voltage", units="V")
        self.__raw_spectrogram_preview_image_view = ImageView(view=plot_item)

        self.__raw_spectrogram_preview_image_view.ui.roiBtn.hide()
        self.__raw_spectrogram_preview_image_view.ui.menuBtn.hide()
        self.__raw_spectrogram_preview_image_view.getView().invertY(False)
        self.__raw_spectrogram_preview_image_view.getView().setAspectLocked(False)
        self.__raw_spectrogram_preview_image_view.setColorMap(
            pg.colormap.get("inferno")
        )

        self.__raw_spectrogram_widget = QWidget()
        self.__raw_spectrogram_widget.setLayout(QVBoxLayout())

        self.__spectrogram_worker: Optional[RaActiveConverterDialog.__Worker] = None

        # input regulation
        self.__ui.inputRegulationComboBox.currentIndexChanged.connect(
            self.__ui.inputRegulationStackedWidget.setCurrentIndex
        )

        self.__input_regulation_thermal_phase_shifter_tab = RegulationPhaseShifterTab()
        self.__ui.inputRegulationStackedWidget.addWidget(
            self.__input_regulation_thermal_phase_shifter_tab
        )

        self.__input_regulation_polynomial_tab = RegulationPolynomialTab()
        self.__ui.inputRegulationStackedWidget.addWidget(
            self.__input_regulation_polynomial_tab
        )

        self.__ui.inputRegulationComboBox.addItems(
            ["Thermal Phase Shifter", "Polynomial"]
        )
        self.__ui.inputRegulationComboBox.setCurrentIndex(0)

        # conversion methods
        self.__ui.conversionMethodComboBox.currentIndexChanged.connect(
            self.__ui.conversionMethodStackedWidget.setCurrentIndex
        )

        self.__rctf_tab = ConversionRCTFTab()
        self.__ui.conversionMethodStackedWidget.addWidget(self.__rctf_tab)

        self.__ZPGTF_tab = ConversionZPGTFTab()
        self.__ui.conversionMethodStackedWidget.addWidget(self.__ZPGTF_tab)

        self.__ui.conversionMethodComboBox.addItems(["RC Circuit", "Zero-Pole-Gain"])
        self.__ui.conversionMethodComboBox.setCurrentIndex(0)

        self.__conversion_method_visualize_button = QPushButton("Visualize")
        self.__conversion_method_visualize_button.clicked.connect(
            self.slot_on_wavelength_conversion_plot_clicked
        )
        self.__ui.conversionMethodGroupBox.layout().insertWidget(  # type: ignore
            self.__ui.conversionMethodGroupBox.layout().count() - 1,
            self.__conversion_method_visualize_button,
        )

        self.__conversion_method_graphics_layout_widget = GraphicsLayoutWidget()
        self.__conversion_method_impulse_response_plot = (
            self.__conversion_method_graphics_layout_widget.addPlot(
                title="Impulse Response"
            )
        )
        self.__conversion_method_step_response_plot = (
            self.__conversion_method_graphics_layout_widget.addPlot(
                title="Step Response"
            )
        )
        self.__conversion_method_periodic_response_plot = (
            self.__conversion_method_graphics_layout_widget.addPlot(
                title="Periodic Response"
            )
        )
        self.__ui.conversionMethodGroupBox.layout().insertWidget(  # type: ignore
            self.__ui.conversionMethodGroupBox.layout().count() - 1,
            self.__conversion_method_graphics_layout_widget,
        )

        # Plot Setting
        self.__ui.plotPushButton.clicked.connect(self.slot_on_plot_FSR_clicked)

        # Output Path
        self.__ui.outputPathPushButton.clicked.connect(
            self.slot_select_output_path_clicked
        )
        default_output_path = os.path.join(
            self.__folder_path, OUTPUT_SUBDIR_DEFAULT_NAME
        )
        self.__ui.outputPathComboBox.setCurrentText(default_output_path)
        self.__ui.outputPathComboBox.addItem(default_output_path)

        # load csv config
        if os.path.exists(
            config_path := os.path.join(self.__folder_path, CONFIG_CSV_DEFAULT_NAME)
        ):
            csv_config = ConverterConfig.from_csv(config_path)
            self.__ui.skipRowsSpinBox.setValue(csv_config.skip_row)
            self.__ui.skipColumnsSpinBox.setValue(csv_config.skip_column)
            self.__ui.rawRampChannelSpinBox.setValue(csv_config.ramp_channel)
            self.__ui.rampSymmetryDoubleSpinBox.setValue(
                csv_config.ramp_signal_symmetry
            )
            self.__ui.rampVMinDoubleSpinBox.setValue(csv_config.v_min)
            self.__ui.rampVMaxDoubleSpinBox.setValue(csv_config.v_max)
            self.__ui.conversionMethodOutputOffsetDoubleSpinBox.setValue(
                csv_config.laser_wavelength
            )
            if csv_config.method1:
                self.__ui.inputRegulationComboBox.setCurrentIndex(1)
                self.__input_regulation_polynomial_tab.a_array_line_edit.setText(
                    str(csv_config.a_array)
                )
                self.__input_regulation_polynomial_tab.x_array_line_edit.setText(
                    str(csv_config.x_array)
                )
            elif csv_config.method2:
                self.__ui.inputRegulationComboBox.setCurrentIndex(0)
                self.__input_regulation_thermal_phase_shifter_tab.fsr_double_spinbox.setValue(
                    csv_config.fsr * 1e9
                )
                self.__input_regulation_thermal_phase_shifter_tab.p_fsr_double_spinbox.setValue(
                    csv_config.p_fsr * 1e3
                )
                self.__input_regulation_thermal_phase_shifter_tab.r_double_spinbox.setValue(
                    csv_config.r_heater
                )
                self.__input_regulation_thermal_phase_shifter_tab.v_offset_double_spinbox.setValue(
                    csv_config.v_offset
                )

            # calculate r, c arrays from csv config
            rc_length = max(
                len(csv_config.r_array),
                len(csv_config.c_array),
                len(csv_config.tau_array),
            )
            r_array_pad = csv_config.r_array + [None] * (
                rc_length - len(csv_config.r_array)
            )
            c_array_pad = csv_config.c_array + [None] * (
                rc_length - len(csv_config.c_array)
            )
            tau_array_pad = csv_config.tau_array + [None] * (
                rc_length - len(csv_config.tau_array)
            )

            r_array = []
            c_array = []
            for r, c, tau in zip(r_array_pad, c_array_pad, tau_array_pad):
                match r, c, tau:
                    case float(r), float(c), None:
                        r_array.append(r)
                        c_array.append(c)
                    case float(r), None, float(tau):
                        r_array.append(r)
                        c_array.append(tau / r)
                    case None, float(c), float(tau):
                        r_array.append(tau / c)
                        c_array.append(c)
                    case _:
                        raise ValueError(
                            f"Invalid R C Tau array. Received r={r}, c={c}, tau={tau}"
                        )

            self.__rctf_tab.rs_line_edit.setText(str(r_array))
            self.__rctf_tab.cs_line_edit.setText(str(c_array))
        else:  # no config file, use ui default values
            pass

    # Custom Slots
    def slot_on_sweep_raw_preview_setting_load(self):
        self.__ui.plotTabWidget.setEnabled(False)
        self.__ui.rawPreviewFileComboBox.blockSignals(True)

        pattern = re.compile(self.__ui.rawRegexLineEdit.text())

        # set up csv reader
        self.__csv_reader = RampUpSweepCSVReader2(
            folder_path=self.__folder_path,
            pattern=pattern,
            skip_rows=self.__ui.skipRowsSpinBox.value(),
            skip_columns=self.__ui.skipColumnsSpinBox.value(),
            ramp_channel=self.__ui.rawRampChannelSpinBox.value() - 1,
        )

        # set up file list
        filenames = sorted(
            list(
                filter(lambda x: pattern.match(x), iter(os.listdir(self.__folder_path)))
            ),
            key=lambda x: int(pattern.match(x).group(1)),  # type: ignore
        )
        self.__ui.rawPreviewFileComboBox.clear()
        self.__ui.rawPreviewFileComboBox.addItems(filenames)

        # set up plot tabs according to the number of channels
        self.__ui.plotTabWidget.clear()
        channel_num = self.__csv_reader.data_shape[0]
        for i in range(channel_num):
            self.__ui.plotTabWidget.addTab(
                RaActiveConverterFSRTabWidget(), f"Channel {i+1}"
            )

        self.__ui.rawSpectrogramPlotPushButton.setEnabled(True)
        self.__ui.plotPushButton.setEnabled(True)

        self.__ui.rawPreviewFileComboBox.blockSignals(False)
        self.slot_on_sweep_raw_preview_file_changed()

    def slot_on_sweep_raw_preview_file_changed(self):
        self.__sweep_raw_preview_widget_data_plot.clear()
        self.__sweep_raw_preview_widget_ramp_plot.clear()

        # get CSV data from selected file
        csv_data = CSVData(
            file_path=os.path.join(
                self.__folder_path, self.__ui.rawPreviewFileComboBox.currentText()
            ),
            skip_rows=self.__csv_reader.skip_rows,
            skip_columns=self.__csv_reader.skip_columns,
            ramp_channel=self.__csv_reader.ramp_channel,
        )

        # plot sweep data and ramp data
        color_palette = cycle(["r", "g", "b", "c", "m", "y", "k"])
        for i, channel in enumerate(csv_data.data):
            self.__sweep_raw_preview_widget_data_plot.plot(
                channel, pen=next(color_palette), name=f"Channel {i+1}"
            )
        self.__sweep_raw_preview_widget_ramp_plot.plot(csv_data.ramp)

        # if plot tab widget is enabled, update converted sweep stream data
        if self.__ui.plotTabWidget.isEnabled():
            conversion_tab: ConversionTabBase = self.__ui.conversionMethodStackedWidget.currentWidget()  # type: ignore
            system = conversion_tab.to_lti()

            v_min = self.__ui.rampVMinDoubleSpinBox.value()
            v_max = self.__ui.rampVMaxDoubleSpinBox.value()
            width = self.__ui.rampSymmetryDoubleSpinBox.value() / 100
            freq = self.__ui.rampFrequencyDoubleSpinBox.value()

            t_final = 500 / freq
            len_period = 400
            t = np.arange(0, t_final, 1 / freq / len_period)

            voltage = (sawtooth(2 * np.pi * freq * t, width) + 1) / 2  # type: ignore
            voltage *= v_max - v_min
            voltage += v_min

            regulation_tab: RegulationTabBase = self.__ui.inputRegulationStackedWidget.currentWidget()  # type: ignore
            regulation_function = regulation_tab.to_regulate_function()

            input = regulation_function(voltage)  # type: ignore

            t, y, x = lsim(system, input, t)
            y = y[-len_period:]

            polarity = (
                1 if self.__ui.conversionMethodPolarityComboBox.currentIndex() else -1
            )

            ref = (
                polarity * y
                + self.__ui.conversionMethodOutputOffsetDoubleSpinBox.value()
            )

            selected_file_basename = self.__ui.rawPreviewFileComboBox.currentText()
            pattern = re.compile(self.__ui.rawRegexLineEdit.text())
            file_index = pattern.match(selected_file_basename).group(1)  # type: ignore
            pattern2 = re.compile(selected_file_basename.replace(file_index, f"({file_index})"))  # type: ignore

            reader = RampUpSweepCSVReader2(
                self.__folder_path,
                pattern2,
                self.__ui.skipRowsSpinBox.value(),
                self.__ui.skipColumnsSpinBox.value(),
                self.__ui.rawRampChannelSpinBox.value() - 1,
            )

            def generate_equalized_number(
                data_start_stop: tuple[NDArray, tuple[int, int]],
                ref: NDArray,
                polarity: int,
            ):
                data, (start, stop) = data_start_stop
                power_number_2d = [[] for i in range(data.shape[0])]
                for i, channel in enumerate(data):
                    ref_interp = np.interp(
                        np.linspace(0, 1, len(channel)),
                        np.linspace(0, 1, len(ref)),
                        ref,
                    )

                    index = np.argmin(ref_interp * polarity)
                    power = channel[index:]
                    wavelength = ref_interp[index:]

                    indices = np.argsort(wavelength)
                    wavelength = wavelength[indices]
                    power = power[indices]

                    wavelength -= np.min(wavelength)
                    wavelength /= np.max(wavelength) - np.min(wavelength)
                    wavelength *= stop - start
                    wavelength += start

                    power_number_2d[i] = [wavelength, power]

                return power_number_2d

            y_2d = reduce(
                lambda acc, x: np.array(
                    [np.hstack((a, x[i])) for i, a in enumerate(acc)]
                ),
                starmap(
                    generate_equalized_number,
                    zip(
                        reader,
                        repeat(ref),
                        repeat(polarity),
                    ),
                ),
                np.array(
                    [np.array([[], []]) for _ in range(self.__ui.plotTabWidget.count())]
                ),
            )

            for i in range(self.__ui.plotTabWidget.count()):
                tab: RaActiveConverterFSRTabWidget = self.__ui.plotTabWidget.widget(i)  # type: ignore
                tab.set_stream_plot(y_2d[i].T)

    def slot_on_plot_spectrogram_clicked(self):
        interp_len = self.__ui.rawSpectrogramInterpolateSpinBox.value()

        def get_spectrogram_data():
            with Pool() as pool:
                return np.array(
                    list(
                        pool.starmap(
                            _interpolate_2d_spectrogram_data,
                            zip(
                                islice(map(lambda x: x[0], self.__csv_reader), 1000),
                                repeat(interp_len),
                            ),
                        )
                    )
                ).swapaxes(0, 1)

        if (
            self.__spectrogram_worker is not None
            and self.__spectrogram_worker.isRunning()
        ):
            return
        else:
            self.__ui.rawSpectrogramPlotPushButton.setEnabled(False)
            self.__ui.rawPreviewFileComboBox.setEnabled(False)

            self.__spectrogram_worker = self.__Worker(f=get_spectrogram_data)
            self.__spectrogram_worker.finished.connect(self.slot_plot_spectrogram_done)
            self.__spectrogram_worker.start()

    def slot_plot_spectrogram_done(self):
        self.__ui.rawSpectrogramPlotPushButton.setEnabled(True)
        self.__ui.rawPreviewFileComboBox.setEnabled(True)
        data_interpolated = self.__spectrogram_worker.result  # type: ignore
        self.__spectrogram_worker.deleteLater()  # type: ignore
        self.__spectrogram_worker = None

        while self.__raw_spectrogram_widget.layout().count():
            self.__raw_spectrogram_widget.layout().takeAt(0).widget().deleteLater()

        view_box = None
        for i, channel in enumerate(data_interpolated):
            plot_item = PlotItem()
            plot_item.setLabel(axis="bottom", text="Sweep Number")
            plot_item.setLabel(axis="left", text="Voltage", units="V")
            plot_item.setTitle(
                f"{self.__ui.rawPreviewFileComboBox.currentText()} Channel {i+1}"
            )
            if view_box is None:
                view_box = plot_item.getViewBox()
            else:
                plot_item.setXLink(view_box)
                plot_item.setYLink(view_box)

            image_view = ImageView(view=plot_item)
            image_view.ui.roiBtn.hide()
            image_view.ui.menuBtn.hide()
            image_view.getView().invertY(False)
            image_view.getView().setAspectLocked(False)
            image_view.setColorMap(pg.colormap.get("inferno"))
            image_view.setImage(channel)
            tr = QTransform()
            tr.scale(
                1,
                (
                    self.__ui.rampVMaxDoubleSpinBox.value()
                    - self.__ui.rampVMinDoubleSpinBox.value()
                )
                / channel.shape[1],
            )
            tr.translate(0, self.__ui.rampVMinDoubleSpinBox.value())
            image_view.imageItem.setTransform(tr)
            image_view.getView().autoRange()

            self.__raw_spectrogram_widget.layout().addWidget(image_view)

        self.__raw_spectrogram_widget.show()

    def slot_on_wavelength_conversion_plot_clicked(self):
        for i in (
            self.__conversion_method_impulse_response_plot,
            self.__conversion_method_step_response_plot,
            self.__conversion_method_periodic_response_plot,
        ):
            i.clear()

        conversion_tab: ConversionTabBase = self.__ui.conversionMethodStackedWidget.currentWidget()  # type: ignore
        system = conversion_tab.to_lti()

        self.__conversion_method_impulse_response_plot.plot(*impulse2(system))
        self.__conversion_method_impulse_response_plot.getAxis("bottom").setLabel(
            units="s"
        )
        self.__conversion_method_step_response_plot.plot(*step(system))
        self.__conversion_method_step_response_plot.getAxis("bottom").setLabel(
            units="s"
        )

        v_min = self.__ui.rampVMinDoubleSpinBox.value()
        v_max = self.__ui.rampVMaxDoubleSpinBox.value()
        width = self.__ui.rampSymmetryDoubleSpinBox.value() / 100
        freq = self.__ui.rampFrequencyDoubleSpinBox.value()

        t_final = 500 / freq
        len_period = 200
        t = np.arange(0, t_final, 1 / freq / len_period)

        voltage = (sawtooth(2 * np.pi * freq * t, width) + 1) / 2  # type: ignore
        voltage *= v_max - v_min
        voltage += v_min

        regulation_tab: RegulationTabBase = self.__ui.inputRegulationStackedWidget.currentWidget()  # type: ignore
        regulation_function = regulation_tab.to_regulate_function()

        input = regulation_function(voltage)  # type: ignore

        t, y, x = lsim(system, input, t)
        t_plot = t[-len_period * 2 :]
        t_plot -= t_plot[0]
        y_plot = y[-len_period * 2 :]
        voltage_plot = voltage[-len_period * 2 :]
        input_plot: list[float] = input[-len_period * 2 :]  # type: ignore

        self.__conversion_method_periodic_response_plot.addLegend()
        self.__conversion_method_periodic_response_plot.getAxis("bottom").setLabel(
            units="s"
        )
        self.__conversion_method_periodic_response_plot.plot(
            t_plot,
            voltage_plot,
            name="voltage ramp",
            pen={"color": "r", "style": Qt.PenStyle.DashLine},
        )
        self.__conversion_method_periodic_response_plot.plot(
            t_plot,
            input_plot,
            name="input",
            pen={"color": "g", "style": Qt.PenStyle.DashLine},
        )
        self.__conversion_method_periodic_response_plot.plot(
            t_plot,
            y_plot,
            name="output",
        )

    def slot_on_plot_FSR_clicked(self):
        conversion_tab: ConversionTabBase = self.__ui.conversionMethodStackedWidget.currentWidget()  # type: ignore
        system = conversion_tab.to_lti()

        v_min = self.__ui.rampVMinDoubleSpinBox.value()
        v_max = self.__ui.rampVMaxDoubleSpinBox.value()
        width = self.__ui.rampSymmetryDoubleSpinBox.value() / 100
        freq = self.__ui.rampFrequencyDoubleSpinBox.value()

        t_final = 500 / freq
        len_period = 400
        t = np.arange(0, t_final, 1 / freq / len_period)

        voltage = (sawtooth(2 * np.pi * freq * t, width) + 1) / 2  # type: ignore
        voltage *= v_max - v_min
        voltage += v_min

        regulation_tab: RegulationTabBase = self.__ui.inputRegulationStackedWidget.currentWidget()  # type: ignore
        regulation_function = regulation_tab.to_regulate_function()

        input = regulation_function(voltage)  # type: ignore

        t, y, x = lsim(system, input, t)
        y = y[-len_period:]

        polarity = (
            1 if self.__ui.conversionMethodPolarityComboBox.currentIndex() else -1
        )

        ref = polarity * y + self.__ui.conversionMethodOutputOffsetDoubleSpinBox.value()

        def f():
            channel_num = self.__csv_reader.data_shape[0]  # type: ignore
            with Pool() as pool:
                return list(
                    reduce(
                        lambda acc, x: [
                            channel + x[i] for i, channel in enumerate(acc)
                        ],
                        pool.starmap(
                            _sweep_2d_data_to_wl_fsr,
                            zip(
                                map(lambda x: x[0], self.__csv_reader),
                                repeat(ref),
                                repeat(polarity),
                            ),
                        ),
                        [[] for i in range(channel_num)],
                    )
                )

        self.__ui.plotPushButton.setEnabled(False)
        for i in range(self.__ui.plotTabWidget.count()):
            tab: RaActiveConverterFSRTabWidget = self.__ui.plotTabWidget.widget(i)  # type: ignore
            tab.clear()

        self.__fsr_worker = self.__Worker(f)
        self.__fsr_worker.finished.connect(self.slot_on_plot_FSR_finished)
        self.__fsr_worker.start()

    def slot_on_plot_FSR_finished(self):
        self.__ui.plotPushButton.setEnabled(True)
        self.__ui.plotTabWidget.setEnabled(True)
        data = self.__fsr_worker.result
        for i, channel in enumerate(data):
            tab: RaActiveConverterFSRTabWidget = self.__ui.plotTabWidget.widget(i)  # type: ignore
            points = np.array(channel).T
            tab.set_scatter_plot(
                points[0],
                points[1],
                fit=self.__ui.plotTrendlineCheckBox.isChecked(),
                order=self.__ui.plotTrendlineOrderSpinBox.value(),
                outlier_range=self.__ui.plotTrendlineOutlierRangeDoubleSpinBox.value()
                * 1e-3,
            )

        # trigger this slot to update the equalized stream plot
        self.slot_on_sweep_raw_preview_file_changed()

    def slot_select_output_path_clicked(self):
        path = QFileDialog.getExistingDirectory(dir=self.__folder_path)
        if path:
            if path not in [
                self.__ui.outputPathComboBox.itemText(i)
                for i in range(self.__ui.outputPathComboBox.count())
            ]:
                self.__ui.outputPathComboBox.addItem(path)
            self.__ui.outputPathComboBox.setCurrentText(path)

    # Dialog Slots
    def accept(self):
        if self.__csv_reader is None:
            logger.info("Conversion failed with no CSV rules loaded.")
            return

        conversion_tab: ConversionTabBase = self.__ui.conversionMethodStackedWidget.currentWidget()  # type: ignore
        system = conversion_tab.to_lti()

        v_min = self.__ui.rampVMinDoubleSpinBox.value()
        v_max = self.__ui.rampVMaxDoubleSpinBox.value()
        width = self.__ui.rampSymmetryDoubleSpinBox.value() / 100
        freq = self.__ui.rampFrequencyDoubleSpinBox.value()

        t_final = 50
        len_period = 400
        t = np.arange(0, t_final, 1 / freq / len_period)

        voltage = (sawtooth(2 * np.pi * freq * t, width) + 1) / 2  # type: ignore
        voltage *= v_max - v_min
        voltage += v_min

        regulation_tab: RegulationTabBase = self.__ui.inputRegulationStackedWidget.currentWidget()  # type: ignore
        regulation_function = regulation_tab.to_regulate_function()

        input = regulation_function(voltage)  # type: ignore

        t, y, x = lsim(system, input, t)
        y = y[-len_period:]

        polarity = (
            1 if self.__ui.conversionMethodPolarityComboBox.currentIndex() else -1
        )

        ref = polarity * y + self.__ui.conversionMethodOutputOffsetDoubleSpinBox.value()

        interp_len = self.__ui.rawSpectrogramInterpolateSpinBox.value()

        def f():
            with Pool() as pool:
                return list(
                    pool.starmap(
                        _sweep_2d_data_to_passive_format,
                        zip(
                            map(lambda x: x[0], self.__csv_reader),
                            repeat(ref),
                            repeat(polarity),
                            repeat(interp_len),
                        ),
                    )
                )

        self.__convert_worker = self.__Worker(f)
        self.__convert_worker.finished.connect(self.slot_on_conversion_done)

        csv_config_path = os.path.join(self.__folder_path, CONFIG_CSV_DEFAULT_NAME)
        csv_config = ConverterConfig(
            skip_row=self.__ui.skipRowsSpinBox.value(),
            skip_column=self.__ui.skipColumnsSpinBox.value(),
            ramp_channel=self.__ui.rawRampChannelSpinBox.value(),
            ramp_signal_symmetry=self.__ui.rampSymmetryDoubleSpinBox.value(),
            v_min=self.__ui.rampVMinDoubleSpinBox.value(),
            v_max=self.__ui.rampVMaxDoubleSpinBox.value(),
            laser_wavelength=self.__ui.conversionMethodOutputOffsetDoubleSpinBox.value(),
            wavelength_conversion_methods=None,
            method1=self.__ui.inputRegulationStackedWidget.currentWidget()
            is self.__input_regulation_polynomial_tab,
            a_array=list(
                eval(self.__input_regulation_polynomial_tab.a_array_line_edit.text())
            ),
            x_array=list(
                eval(self.__input_regulation_polynomial_tab.x_array_line_edit.text())
            ),
            method2=self.__ui.inputRegulationStackedWidget.currentWidget()
            is self.__input_regulation_thermal_phase_shifter_tab,
            fsr=self.__input_regulation_thermal_phase_shifter_tab.fsr_double_spinbox.value()
            * 1e-9,
            p_fsr=self.__input_regulation_thermal_phase_shifter_tab.p_fsr_double_spinbox.value()
            * 1e-3,
            r_heater=self.__input_regulation_thermal_phase_shifter_tab.r_double_spinbox.value(),
            v_offset=self.__input_regulation_thermal_phase_shifter_tab.v_offset_double_spinbox.value(),
            thermal_response=None,
            r_array=list(eval(self.__rctf_tab.rs_line_edit.text())),
            c_array=list(eval(self.__rctf_tab.cs_line_edit.text())),
            tau_array=list(),
            gain=self.__rctf_tab.gain_double_spinbox.value(),
        )
        csv_config.to_csv(csv_config_path)
        logger.info(f"RA-Active-Converter config csv file saved to {csv_config_path}")

        self.setEnabled(False)
        self.__convert_worker.start()

    def slot_on_conversion_done(self):
        result = self.__convert_worker.result
        output_dir = self.__ui.outputPathComboBox.currentText()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i, d in enumerate(result):
            savemat(os.path.join(output_dir, f"laser_sweep_{i}.mat"), d)
        super().accept()
