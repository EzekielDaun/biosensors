import logging
import os
import re
import sys

import pyqtgraph as pg
from PySide6.QtCore import QDir, Qt, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFileSystemModel,
    QListWidgetItem,
    QMainWindow,
    QVBoxLayout,
)

from ..core.passive_tools import PassiveAnalyzer as Analyzer
from ..uic.base.ra_main_window import Ui_RaMainWindow
from ..widgets.base.ra_peak_tracker_widget import RaPeakTrackerWidget
from ..widgets.base.ra_tab_plotter_widget import (
    RaFilePlotterWidget,
    RaSpectrogramPlotterWidget,
)
from .ra_active_converter_dialog import RaActiveConverterDialog

logger = logging.getLogger(__name__)

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class RaMainWindow(QMainWindow):
    __signal_write = Signal(str)

    def __init__(self):
        super().__init__()
        self.__ui = Ui_RaMainWindow()
        self.__ui.setupUi(self)

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.__ui.statusbar.showMessage("Retrospective Analysis")

        # initialize file treeview
        model = QFileSystemModel()
        model.setFilter(
            QDir.Filter.AllEntries | QDir.Filter.NoDot | QDir.Filter.AllDirs
        )
        model.setRootPath(QDir.rootPath())
        self.__ui.treeView.setModel(model)
        self.__ui.treeView.setRootIndex(model.index(os.path.expanduser("~")))

        # file plotter
        self.__file_plotter_widget = RaFilePlotterWidget()
        self.__ui.splitter.insertWidget(1, self.__file_plotter_widget)
        self.__ui.splitter.setStretchFactor(1, 2)

        # spectrum plotter
        # intended to be popped up so not in any layout
        self.__folder_plotter = RaSpectrogramPlotterWidget()
        self.__folder_plotter.signal_spectrograms_work_done.connect(
            self.__ui.spectrogramButton.setEnabled
        )

        # peak tracker
        self.__peak_tracker_widget = RaPeakTrackerWidget()
        self.__ui.peakTrackerWidget.setLayout(QVBoxLayout())
        self.__ui.peakTrackerWidget.layout().addWidget(self.__peak_tracker_widget)
        self.__peak_tracker_widget.signal_work_done.connect(
            self.__ui.trackPeakButton.setEnabled
        )
        self.__peak_tracker_widget.signal_work_done.connect(
            self.__ui.saveResultsButton.setEnabled
        )
        self.__peak_tracker_widget.signal_fsr_er_q_work_done.connect(
            self.__ui.FSRERQButton.setEnabled
        )

        # Redirect stdout and stderr to log panel
        self.__signal_write.connect(self.slot_log_write)
        sys.stdout = self
        sys.stderr = self

        self.__ui.analyzerSettingsGroupBox.setEnabled(False)
        self.__ui.plotSpectrogramsGroupBox.setEnabled(False)
        self.__ui.peakTracingGroupBox.setEnabled(False)

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
    def slot_open_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(
            dir=os.path.expanduser("~"),
        )
        if folder_path == "":
            self.__ui.statusbar.showMessage("Retrospective Analysis - Open cancelled")
        else:
            tree_view = self.__ui.treeView
            model: QFileSystemModel = tree_view.model()  # type: ignore
            tree_view.setRootIndex(model.index(folder_path))
            self.__ui.statusbar.showMessage(f"Retrospective Analysis - {folder_path}")
            os.chdir(folder_path)

            # clear
            self.__ui.powerListWidget.clear()
            self.__ui.peakTrackerPowerListWidget.clear()
            self.__ui.timeStampComboBox.clear()
            self.__peak_tracker_widget.clear()
            self.__file_plotter_widget.clear()

            # setup timestamp selector combo box
            pat = re.compile(r".*time.*\.csv")
            for f in filter(lambda x: pat.match(x), iter(os.listdir(folder_path))):
                self.__ui.timeStampComboBox.addItem(str(f))

            self.__ui.analyzerSettingsGroupBox.setEnabled(True)
            self.__ui.plotSpectrogramsGroupBox.setEnabled(False)
            self.__ui.peakTracingGroupBox.setEnabled(False)
            self.__ui.saveResultsButton.setEnabled(False)

    def slot_action_active_converter_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(
            dir=os.path.expanduser("~"),
        )
        if folder_path == "":
            self.__ui.statusbar.showMessage("Retrospective Analysis - Open cancelled")
        else:
            dialog = RaActiveConverterDialog(folder_path, self)
            dialog.show()

    def slot_file_changed(self, model_index):
        tree_view = self.__ui.treeView
        model: QFileSystemModel = tree_view.model()  # type: ignore
        file_path = model.filePath(model_index)
        file_name = os.path.basename(file_path)
        _, file_ext = os.path.splitext(file_name)
        if model.isDir(model.index(file_path)):
            tree_view.setRootIndex(model.index(file_path))
            self.__ui.statusbar.showMessage(f"Retrospective Analysis - {file_path}")
        elif file_ext != ".mat":
            logger.error(f"{file_name} is not a matlab workspace file")
        else:
            self.__file_plotter_widget.update(
                file_path,
                r2_threshold=self.__ui.r2ThresholdDoubleSpinBox.value(),
                max_n100dBm_points=self.__ui.n100dBmToleranceSpinBox.value(),
            )

    def slot_load_analyzer(self):
        # clear power list widget
        self.__ui.powerListWidget.clear()
        self.__ui.peakTrackerPowerListWidget.clear()
        # clear peak tracker
        self.__peak_tracker_widget.clear()

        # load analyzer parameters
        try:
            pattern = eval(self.__ui.patternLineEdit.text())
            wavelength_multiplier = float(
                eval(self.__ui.wavelengthMultiplierLineEdit.text())
            )
            time_multiplier = float(eval(self.__ui.timeMultiplierLineEdit.text()))
        except Exception as e:
            logger.error(f"{e}")
            raise e

        path = self.__ui.treeView.model().filePath(  # type: ignore
            self.__ui.treeView.rootIndex()
        )
        timestamp = self.__ui.timeStampComboBox.currentText()
        try:
            timestamp = float(timestamp)
        except ValueError as e:  # if parse float failed
            if re.match(r".*\.csv", timestamp):
                pass
            else:
                logger.error(f"'{timestamp}' is not a number or a csv file")
                raise e

        self.__analyzer = Analyzer(
            path, timestamp, pattern, wavelength_multiplier, time_multiplier
        )

        file_num, power_num = self.__analyzer.info()
        logger.info(f"{path} has {file_num} files with {power_num} power channels")

        # update peak tracker output path combo box
        self.__ui.peakTracingOutputPathComboBox.setCurrentText(path)
        self.__ui.peakTracingOutputPathComboBox.addItem(path)

        # update spectrogram plotter start/stop values
        self.__ui.sampleStartSpinBox.setMaximum(file_num)
        self.__ui.sampleStopSpinBox.setMinimum(2)
        self.__ui.sampleStopSpinBox.setMaximum(file_num)
        self.__ui.sampleStopSpinBox.setValue(file_num)

        # update peak tracing start/stop values
        self.__ui.peakTracingStartSpinBox.setMaximum(file_num)
        self.__ui.peakTracingStopSpinBox.setMaximum(file_num)
        self.__ui.peakTracingStopSpinBox.setValue(file_num)

        # add power channels to power list widget
        for i in range(power_num):
            item = QListWidgetItem()
            checkbox = QCheckBox(f"Power {i+1}")
            self.__ui.powerListWidget.addItem(item)
            self.__ui.powerListWidget.setItemWidget(item, checkbox)

            item = QListWidgetItem()
            checkbox = QCheckBox(f"Power {i+1}")
            checkbox.setChecked(True)
            self.__ui.peakTrackerPowerListWidget.addItem(item)
            self.__ui.peakTrackerPowerListWidget.setItemWidget(item, checkbox)

        self.__ui.plotSpectrogramsGroupBox.setEnabled(True)
        self.__ui.peakTracingGroupBox.setEnabled(True)

    # Spectrogram plotting slots
    def slot_plot_spectrogram(self):
        self.__folder_plotter.analyzer = self.__analyzer
        lw = self.__ui.powerListWidget
        powers = {i for i in range(lw.count()) if lw.itemWidget(lw.item(i)).checkState() == Qt.Checked}  # type: ignore
        if len(powers) != 0:
            self.__folder_plotter.plot_spectrograms(
                powers,
                self.__ui.sampleStepSpinBox.value(),
                self.__ui.sampleStartSpinBox.value() - 1,
                self.__ui.sampleStopSpinBox.value(),
                self.__ui.xTicksSpinBox.value(),
                self.__ui.yTicksSpinBox.value(),
                self.__ui.powerUnitLineEdit.text(),
                self.__ui.timeUnitLineEdit.text(),
                self.__ui.wavelengthUnitLineEdit.text(),
            )
            self.__folder_plotter.show()
            logger.info("Spectrogram plotting started!")
        else:
            logger.warning("No power channel selected!")

    def slot_spectrogram_select_all(self):
        lw = self.__ui.powerListWidget
        for i in range(lw.count()):
            lw.itemWidget(lw.item(i)).setChecked(True)  # type: ignore

    def slot_spectrogram_unselect_all(self):
        lw = self.__ui.powerListWidget
        for i in range(lw.count()):
            lw.itemWidget(lw.item(i)).setChecked(False)  # type: ignore

    def slot_spectrogram_on_start_spinbox_change(self, value: int):
        file_num, _ = self.__analyzer.info()
        self.__ui.sampleStopSpinBox.setMinimum(min(max(2, value + 1), file_num))

    def slot_spectrogram_on_stop_spinbox_change(self, value: int):
        self.__ui.sampleStartSpinBox.setMaximum(max(1, value - 1))

    # Peak tracking slots
    def slot_track_peak(self):
        lw = self.__ui.peakTrackerPowerListWidget
        powers = {i for i in range(lw.count()) if lw.itemWidget(lw.item(i)).checkState() == Qt.Checked}  # type: ignore
        self.__peak_tracker_widget.plot_initial(
            self.__analyzer,
            powers,
            (
                self.__ui.peakTracingStartSpinBox.value() - 1,
                self.__ui.peakTracingStopSpinBox.value(),
                self.__ui.peakTracingStepSpinBox.value(),
            ),
            self.__ui.timeUnitLineEdit.text(),
            self.__ui.wavelengthUnitLineEdit.text(),
            self.__ui.powerUnitLineEdit.text(),
            self.__ui.r2ThresholdDoubleSpinBox.value(),
            self.__ui.n100dBmToleranceSpinBox.value(),
        )

    def slot_save_results(self):
        output_path = os.path.join(
            self.__ui.peakTracingOutputPathComboBox.currentText(), "RA_result"
        )
        os.makedirs(output_path, exist_ok=True)
        self.__peak_tracker_widget.save_results(output_path)

    def slot_peak_tracking_select_all(self):
        lw = self.__ui.peakTrackerPowerListWidget
        for i in range(lw.count()):
            lw.itemWidget(lw.item(i)).setChecked(True)  # type: ignore

    def slot_peak_tracking_unselect_all(self):
        lw = self.__ui.peakTrackerPowerListWidget
        for i in range(lw.count()):
            lw.itemWidget(lw.item(i)).setChecked(False)  # type: ignore

    def slot_peak_tracking_select_output_path(self):
        path = QFileDialog.getExistingDirectory(
            dir=self.__ui.treeView.model().filePath(  # type: ignore
                self.__ui.treeView.rootIndex()
            ),
        )
        if path != "":
            self.__ui.peakTracingOutputPathComboBox.setCurrentText(path)
            self.__ui.peakTracingOutputPathComboBox.addItem(path)

    def slot_peak_tracking_on_start_spinbox_change(self, value: int):
        file_num, _ = self.__analyzer.info()
        self.__ui.peakTracingStopSpinBox.setMinimum(min(max(2, value + 1), file_num))

    def slot_peak_tracking_on_stop_spinbox_change(self, value: int):
        self.__ui.peakTracingStartSpinBox.setMaximum(max(1, value - 1))

    # FSR ER Q slots
    def slot_fsr_er_q(self):
        lw = self.__ui.peakTrackerPowerListWidget
        powers = {i for i in range(lw.count()) if lw.itemWidget(lw.item(i)).checkState() == Qt.Checked}  # type: ignore
        output_path = os.path.join(
            self.__ui.peakTracingOutputPathComboBox.currentText(), "RA_result"
        )
        os.makedirs(output_path, exist_ok=True)
        self.__peak_tracker_widget.fsr_er_q(
            self.__analyzer,
            powers,
            (
                self.__ui.peakTracingStartSpinBox.value() - 1,
                self.__ui.peakTracingStopSpinBox.value(),
                self.__ui.peakTracingStepSpinBox.value(),
            ),
            output_path,
        )
