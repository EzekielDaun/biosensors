import datetime
import random
import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Signal, QObject, QRunnable, QThreadPool, Slot
import json
import logging
from MultiSweep.deviceTab import ConnectWindow
from MultiSweep.parameterTab import ParamTableWindow
from MultiSweep.runTab import RunWindow
from MultiSweep.multi_sweep_v2 import MultiSweep
import sys
import traceback
import pprint
from fineAlign_wN77 import fineAlign
import time
import os
import psutil
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pyqtgraph as pg

logger = logging.getLogger(__name__)


class LogSignal(QObject):
    log = Signal(str)


class Log(logging.Handler, QObject):
    """
    Class use to log onto the interface
    """

    def __init__(self, parent, emitter):
        super().__init__()
        QObject.__init__(self)
        self.out = sys.stdout
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("Test Log")
        self.layout = QtWidgets.QVBoxLayout(self.window)
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.layout.addWidget(self.widget)
        self.widget.setReadOnly(True)
        self._emitter = emitter
        self._emitter.log.connect(self.insertPlainText_scroll)

    @property
    def emitter(self):
        return self._emitter

    def emit(self, record):
        msg = self.format(record)
        msg = msg + "\n"
        self.emitter.log.emit(msg)

    def write(self, message):
        self.out.write(message)
        self.emitter.log.emit(message)

    def create_log_folder(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        return os.path.join(os.getcwd(), folder_name)

    def insertPlainText_scroll(self, msg):
        self.widget.moveCursor(QtGui.QTextCursor.End)
        self.widget.insertPlainText(msg)
        self.widget.moveCursor(QtGui.QTextCursor.End)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    progress
        int indicating % progress

    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
    initial_sweep = Signal()
    update_graph = Signal(int, dict, list, list, float, int, bool)
    seg_done = Signal(int)
    logs = Signal(str)


class Worker(QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, multisweep):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.multisweep = multisweep
        self.signals = WorkerSignals()
        self.is_paused = False
        self.is_running = True

        # Add the callback to our kwargs

    @Slot()
    def run(self):
        try:
            self.multisweep.update_config()
            self.multisweep.turnon_instruments()

            print("Starting FineAlign...")
            self.multisweep.run_fine_align(
                self.multisweep.laser,
                self.multisweep.stage,
                self.multisweep.guess_wavelength[0] * 1e-9,
            )

            logging.info("Starting Initial Sweep...")
            self.pause()
            self.signals.initial_sweep.emit()  # Signal to GUI

            while self.is_paused:
                if not self.is_running:
                    return

            i, self.total_sweep, self.total_time, self.abs_time, self.abs_sweep = (
                0,
                0,
                time.time(),
                time.time(),
                1,
            )

            for i in range(self.multisweep.segment_num):
                self.check_memory()

                logging.info("Starting Sweep Experiment Section {}".format(int(i + 1)))
                self.multisweep.set_configurations(i)

                self.seg_sweep, self.seg_time = 0, time.time()
                self.run_multisweep_segment(i)

                if not self.is_running:
                    return self.save_config(
                        i=i, scan=self.seg_sweep, t_seg=self.seg_time
                    )

                self.signals.seg_done.emit(i)  # Signal to GUI

        except Exception as e:
            print(
                "Error occurred during experiment or experiment finished early. Aborting..."
            )
            logging.error(str(e))
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            try:
                self.save_config(i=i, scan=self.seg_sweep, t_seg=self.seg_time)
                self.signals.error.emit((exctype, value, traceback.format_exc()))

            except Exception as e:
                print(e)

        finally:
            self.signals.finished.emit()
            return

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def is_fineAlign(self, res, fa_power):
        self.signals.fa_warning.emit(self.abs_sweep, res, fa_power)
        self.signals.fa_graph.emit(fa_power)

    def run_multisweep_segment(self, i):
        if self.multisweep.path[i] != self.multisweep.path[i - 1] or i == 0:
            self.multisweep.start_segment(i)  # create labels for .csv
            self.total_sweep, self.total_time = 1, time.time()

        while self.is_running:
            temp, res, fa_power, wavelength, power = self.multisweep.multiple_sweeps(
                i, self.total_sweep, self.abs_sweep, self.total_time, self.abs_time
            )

            if res is not None:
                self.signals.update_graph.emit(
                    res, fa_power, wavelength, power, temp, self.abs_sweep, True
                )

            else:
                self.signals.update_graph.emit(
                    res, fa_power, wavelength, power, temp, self.abs_sweep, False
                )

            self.total_sweep += 1
            self.abs_sweep += 1
            self.seg_sweep += 1

            if self.multisweep.is_time:
                if (time.time() - self.seg_time) > (self.multisweep.start_time[i] * 60):
                    return
            else:
                if self.seg_sweep >= self.multisweep.sweep_time[i]:
                    return

            if self.is_paused:
                print("MultiSweep successfully paused")
                while self.is_paused:
                    if not self.is_running:
                        return

    def save_config(self, i=0, scan=None, t_seg=None):
        saved_config = {}
        t_elapse = round(((time.time() - t_seg) / 60), 2)

        for key, val in self.multisweep.config["segment"].items():
            if key == "time":
                if self.multisweep.is_time:
                    val[i] = val[i] - t_elapse
                    saved_config[key] = val[i:]

            elif key == "sweep":
                if not self.multisweep.is_time:
                    val[i] = int(val[i] - scan)
                    saved_config[key] = val[i:]

            elif key != "isTime":
                saved_config[key] = val[i:]

        path = os.path.join(self.multisweep.path[i] + "/saved_config.json")
        with open(path, "w") as outfile:
            json.dump(saved_config, outfile, indent=4)

        logging.info("Current Configurations Saved")
        logging.info(
            "Experiment Stopped - Segment: {} Scan:{} Segment Time: {}".format(
                i, scan, t_elapse * 60
            )
        )

    def check_memory(self):
        cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()[2]

        logging.info("CPU Percent: {}  RAM memory: {}".format(cpu_percent, mem))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.multisweep = MultiSweep()
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical box layout
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        layout.addWidget(self.tabWidget)

        # Set up logs and config
        logSignal = LogSignal()
        logTextBox = Log(self, logSignal)
        logTextBox.widget.setMinimumHeight(200)
        logTextBox.widget.setMaximumHeight(250)
        self.log_widget = logTextBox.window

        self.dock_widget = QtWidgets.QDockWidget("Log", self)
        self.dock_widget.setWidget(self.log_widget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_widget)

        log_folder = logTextBox.create_log_folder(".log")
        print(log_folder)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(log_folder, timestamp)

        logging.basicConfig(
            filename=log_path,
            filemode="w+",
            format="%(asctime)-15s %(levelname)-8s %(message)s",
        )
        logTextBox.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )

        logging.getLogger().setLevel(logging.INFO)
        sys.stdout = logTextBox
        logging.getLogger().addHandler(logTextBox)

        # Set up tabs
        self.deviceTab = ConnectWindow(self.multisweep)
        self.paramTab = ParamTableWindow(self.multisweep)
        self.runTab = RunWindow(self.multisweep)
        self.initialSweep = InitialGraphWindow()

        self.tabWidget.addTab(self.deviceTab, "Device")
        self.tabWidget.addTab(self.paramTab, "Parameters")
        self.tabWidget.addTab(self.runTab, "Run")
        self.tabWidget.setStyleSheet(
            """QGroupBox
                {
                    background-color: rgb(237, 237, 237);
                }
        """
        )

        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)

        # Set up threadpool
        self.threadpool = QThreadPool()
        self.worker = None

        self.deviceTab.confirm_button.clicked.connect(self.confirm_device)
        self.deviceTab.edit_button.clicked.connect(self.edit_device)
        self.runTab.start.clicked.connect(self.start_button_pushed)
        self.runTab.pause.clicked.connect(self.pause_exp)
        self.runTab.resume.clicked.connect(self.resume_exp)
        self.runTab.stop.clicked.connect(self.stop_exp)

        self.showMaximized()

    def confirm_device(self):
        self.deviceTab.confirm_device()

        if self.multisweep.is_OBand:
            before_wl = self.multisweep.config["default"]["startWavelength"]
            self.multisweep.config["default"]["startWavelength"] = 1310
            self.multisweep.config["default"]["endWavelength"] = 1350

            if before_wl != 1310:
                self.paramTab.populate_table(start_col=3, end_col=5)
        else:
            before_wl = self.multisweep.config["default"]["startWavelength"]
            self.multisweep.config["default"]["startWavelength"] = 1545
            self.multisweep.config["default"]["endWavelength"] = 1555

            if before_wl != 1545:
                self.paramTab.populate_table(start_col=3, end_col=5)

        self.paramTab.update_table()
        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setTabEnabled(2, True)

        if (
            self.multisweep.laser
            and self.multisweep.stage in self.multisweep.active_instr
        ):
            self.multisweep.fineAlign = fineAlign(
                self.multisweep.laser, self.multisweep.stage
            )
            self.paramTab.fineAlign = self.multisweep.fineAlign
            self.paramTab.fine_align_panel.fineAlign = self.multisweep.fineAlign
            logging.info(
                "Successfully Establish FineAlign. Users can now apply fineAlign settings to the stage."
            )

        else:
            self.fineAlign = None
            logging.info(
                "Cannot Establish FineAlign and apply settings to the stage. Please connect to Laser and "
                "Corvus Stage."
            )

    def edit_device(self):
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)

    def finalize_config(self):
        self.paramTab.get_config()

        # check values
        self.multisweep.update_config()
        self.multisweep.validate_input()

        print("Configurations Validated...")

    def start_button_pushed(self):
        try:
            self.finalize_config()
            self.runTab.fineAlignLog.clear()

            if len(self.multisweep.active_instr) != len(self.multisweep.confirm_instr):
                logging.error(
                    "Not all devices are connected. Please connect before starting the experiment - "
                    "check: {}".format(self.multisweep.confirm_instr)
                )
            else:
                print("Initializing MultiSweep...")
                self.runTab.restart_graph()
                self.worker = Worker(self.multisweep)
                self.worker.signals.finished.connect(self.thread_complete)
                self.worker.signals.initial_sweep.connect(self.start_initial_sweep)
                self.worker.signals.seg_done.connect(self.seg_done)
                self.worker.signals.update_graph.connect(self.runTab.update_graphs)

                print("== STARTING MULTISWEEP ==")
                self.threadpool.start(self.worker)

                self.runTab.start.setEnabled(False)
                self.runTab.stop.setEnabled(True)
                self.runTab.resume.setEnabled(True)
                self.runTab.pause.setEnabled(True)

        except Exception as e:
            if self.worker is not None:
                self.worker.is_running = False

            print(e)

    def start_initial_sweep(self):
        self.pause_exp()

        fig = plt.figure()
        # TODO: Add sweep speed parameter
        try:
            if self.paramTab.initialSweep.isChecked():
                self.multisweep.laser.sweepStartWvl = (
                    float(self.paramTab.initial_wl.text()) * 1e-9
                )
                self.multisweep.laser.sweepStopWvl = (
                    float(self.paramTab.initial_end.text()) * 1e-9
                )
                self.multisweep.laser.sweepStepWvl = (
                    float(self.paramTab.initial_step.text()) * 1e-9
                )
                self.multisweep.laser.sweepPower = float(
                    self.paramTab.initial_power.text()
                )
                self.speedMap = self.multisweep.speed_map
                self.multisweep.laser.sweepSpeed = self.speedMap[
                    str(self.paramTab.initial_speed.currentText())
                ]
                self.multisweep.laser.sweepInitialRange = float(
                    self.paramTab.range_power.text()
                )
                self.multisweep.laser.sweepRangeDecrement = float(
                    self.paramTab.range_det.text()
                )

                power, wavelength = self.multisweep.initial_sweep(param_dict=True)

            else:
                power, wavelength = self.multisweep.initial_sweep(param_dict=False)

            for index, i in enumerate(power.transpose()):
                plt.plot(wavelength * 1e-9, i, label="Power{}".format(index))

            plt.legend()
            fig.show()

            fig.canvas.mpl_connect("close_event", self.cont_exp)

        except Exception as e:
            logging.error(str(e))
            self.stop_exp()

    def cont_exp(self, event):
        QtGui.QGuiApplication.processEvents()
        print("Initial Sweep Finished. Continuing...")
        self.resume_exp()

    def thread_complete(self):
        print("== MULTISWEEP FINISHED ==")
        self.runTab.start.setEnabled(True)
        self.runTab.stop.setEnabled(False)
        self.runTab.pause.setEnabled(False)
        self.runTab.resume.setEnabled(False)

        self.multisweep.disconnect_instr()

    def pause_exp(self):
        print(
            "MultiSweep pausing. Please wait until the the current sweep and/or fineAlign is finished."
        )
        self.worker.pause()
        self.runTab.resume.setEnabled(True)
        self.runTab.pause.setEnabled(False)

    def resume_exp(self):
        print("MultiSweep Resumed.")
        self.worker.resume()
        self.runTab.resume.setEnabled(False)
        self.runTab.pause.setEnabled(True)

    def stop_exp(self):
        print(
            "MultiSweep stopping. Please wait until the current sweep and/or fineAlign is finished."
        )
        self.worker.is_running = False
        self.runTab.stop.setEnabled(False)
        self.runTab.start.setEnabled(True)

    def seg_done(self, i):
        for j in range(self.paramTab.tableWidget.columnCount()):
            self.paramTab.tableWidget.item(i + 2, j).setBackground(
                QtGui.QColor("lightGray")
            )

    def closeEvent(self, event):
        try:
            print("Disconnecting devices and turning off lasers")
            self.multisweep.disconnect_instr(disconnect=True)

            if self.worker is not None:
                self.worker.is_running = False

            event.accept()

        except Exception as e:
            print(e)


class InitialGraphWindow(QtWidgets.QDialog):
    closed = Signal()
    LINECOLORS = ["r", "g", "b", "c", "m", "y", "y", "r", "g"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph Plot in Pop-up Window")

        # Create a QVBoxLayout to arrange the pyqtgraph plot and close button
        layout = QtWidgets.QVBoxLayout(self)

        # Create a pyqtgraph plot widget
        self.pg_plot_widget = pg.PlotWidget()
        self.pg_plot_widget.setBackground("w")
        self.pg_plot_widget.addLegend()

        # Add the pyqtgraph plot widget to the layout
        layout.addWidget(self.pg_plot_widget)

        # Add the pyqtgraph plot widget and close button to the layout
        layout.addWidget(self.pg_plot_widget)
        layout.addWidget(QtWidgets.QPushButton("Close", clicked=self.close))

    def update_graph(self, power, wavelength):
        for index, i in enumerate(power):
            self.pg_plot_widget.plot(
                wavelength, i, pen=self.LINECOLORS[index], name="Power{}".format(index)
            )

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
