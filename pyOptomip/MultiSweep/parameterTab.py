import os.path

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QTableWidgetItem
import pandas as pd
import logging

logger = logging.getLogger(__name__)
from MultiSweep.ui.multi_connect import Ui_GroupBox
from MultiSweep.ui import multi_param
from MultiSweep.ui.multi_finealign import Ui_Form
import visa
from hp816x_instr import hp816x
from hp816x_N77Det_instr import hp816x_N77Det
from CorvusEco import CorvusEcoClass
import xlsxwriter
import json


class ParamTableWindow(QtWidgets.QGroupBox, multi_param.Ui_Form):
    configMap = dict(
        [
            ("Segment Time (min)", "time"),
            ("# of Sweep", "sweep"),
            ("Output Path", "outputPath"),
            ("Start Wavelength (nm)", "startWavelength"),
            ("End Wavelength (nm)", "endWavelength"),
            ("Sweep Step (nm)", "sweepStep"),
            ("Sweep Speed (nm)", "sweepSpeed"),
            ("Laser Intensity (dBm)", "laserIntensity"),
            ("FineAlign Wavelength (nm)", "fineAlignWavelength"),
            ("TEC1 Temp. [C]", "tec1Temp"),
            ("LDC1 Current (mA)", "ldc1Current"),
        ]
    )
    configMap_rev = dict((v, k) for k, v in configMap.items())
    instr_map = dict(
        [
            (
                "Laser",
                [
                    "Segment Time (min)",
                    "# of Sweep",
                    "Output Path",
                    "Start Wavelength (nm)",
                    "End Wavelength (nm)",
                    "Sweep Step (nm)",
                    "Sweep Speed (nm)",
                    "Laser Intensity (dBm)",
                ],
            ),
            ("Stage", ["Fine Align Wavelength (nm)"]),
            ("TEC", ["TEC1 Temp. [C]"]),
        ]
    )

    fineAlignMap = dict(
        [
            ("Detector Priority", "detectorPriority"),
            ("Laser Power (dBm)", "laserPower"),
            ("Step Size (nm)", "stepSize"),
            ("Power Threshold (dBm)", "powerThreshold"),
            ("Window Size (nm)", "windowSize"),
            ("Optimize Wavelength", "optimizeWL"),
            ("Interval", "interval"),
            ("Use Central Wavelength", "centralWL"),
        ]
    )

    fineAlignMap_rev = dict((v, k) for k, v in fineAlignMap.items())

    def __init__(self, multisweep):
        super(ParamTableWindow, self).__init__()
        self.setupUi(self)

        self.multisweep = multisweep
        # self.config = self.multisweep.config
        self.tableWidget.resizeColumnsToContents()
        self.set_checked()
        self.populate_table()

        self.hp816x_buttons = [
            self.det_1,
            self.det_2,
            self.det_3,
            self.det_4,
            self.det_5,
            self.det_6,
            self.det_7,
            self.det_8,
        ]
        self.n77_buttons = [self.n77_1, self.n77_2, self.n77_3, self.n77_4]

        # Table Buttons
        self.addrow.clicked.connect(self.add_row)
        self.duplicaterow.clicked.connect(self.duplicate_row)
        self.deleterow.clicked.connect(self.delete_row)
        self.reset.clicked.connect(self.populate_table)
        self.sweep.clicked.connect(self.on_toggle)
        self.time.clicked.connect(self.on_toggle)
        self.tableWidget.itemChanged.connect(self.update_static)

        # Excel Buttons
        self.open_config.clicked.connect(self.open_xlsx)
        self.export_config.clicked.connect(self.export_xlsx)

        # Fine Align Settings
        self.initialSweep.setChecked(False)
        self.userWL.toggled.connect(self.user_wavelength)
        self.centralWL.toggled.connect(self.central_wavelength)
        self.settings.clicked.connect(self.fine_align_settings)

        # Initialize Fine Align Settings Window
        self.fine_align_panel = FineAlignWindow(self.multisweep.fineAlign)

        self.det_select.clicked.connect(self.on_toggle_det)
        self.n77_select.clicked.connect(self.on_toggle_det)

    def on_toggle_det(self, state):
        name = self.sender().objectName()

        if name == "det_select":
            for i in self.hp816x_buttons:
                i.setChecked(state)

        elif name == "n77_select":
            for i in self.n77_buttons:
                i.setChecked(state)

    def fine_align_settings(self):
        self.fine_align_panel.detSlot()
        self.fine_align_panel.show()

    def on_toggle(self, state):
        if self.sweep.isChecked():
            self.tableWidget.setHorizontalHeaderItem(
                0, QTableWidgetItem(str("# of Sweep"))
            )
        else:
            self.tableWidget.setHorizontalHeaderItem(
                0, QTableWidgetItem(str("Segment Time (min)"))
            )

    def user_wavelength(self, state):
        column_to_enable = None
        if state:
            for i in range(self.tableWidget.columnCount()):
                header = self.tableWidget.horizontalHeaderItem(i).text()
                if header == "FineAlign Wavelength (nm)":
                    column_to_enable = i

            if column_to_enable:
                for row in range(2, self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row, column_to_enable)

                    if item:
                        item.setBackground(QtGui.QColor("white"))
                        item.setFlags(
                            item.flags() & ~QtCore.Qt.ItemIsSelectable
                            | ~QtCore.Qt.ItemIsEditable
                        )

    def central_wavelength(self, state):
        column_to_disable = None
        if state:
            for i in range(self.tableWidget.columnCount()):
                header = self.tableWidget.horizontalHeaderItem(i).text()
                if header == "FineAlign Wavelength (nm)":
                    column_to_disable = i

            if column_to_disable:
                for row in range(2, self.tableWidget.rowCount()):
                    self.tableWidget.setItem(
                        row, column_to_disable, QTableWidgetItem("")
                    )
                    item = self.tableWidget.item(row, column_to_disable)
                    if item:
                        item.setBackground(QtGui.QColor("lightGray"))
                        item.setFlags(
                            item.flags() & QtCore.Qt.ItemIsSelectable
                            | QtCore.Qt.ItemIsEditable
                        )

    def update_finalign_wavelength(self, item=None):
        if self.centralWL.isChecked():
            self.central_wavelength(True)
        else:
            self.user_wavelength(True)

    def open_xlsx(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", "c:\\")
        path = path[0]

        if os.path.isfile(path):
            if path.endswith(".xlsx"):
                data = pd.read_excel(path)

                if "Laser Intensity (dBm)" not in data.columns:
                    finealign_data = pd.read_excel(path, nrows=2).to_dict("list")
                    logging_data = pd.read_excel(path, skiprows=3).to_dict("list")
                    self.populate_finealign(finealign_data, logging_data)
                    return

                else:
                    data_dict = data.to_dict()

            elif path.endswith(".csv"):
                data = pd.read_csv(path)

                if "Laser Intensity (dBm)" not in data.columns:
                    finealign_data = pd.read_excel(path, nrows=2).to_dict("list")
                    logging_data = pd.read_excel(path, skiprows=3).to_dict("list")
                    self.populate_finealign(finealign_data, logging_data)
                    return

                else:
                    data_dict = data.to_dict()

            elif path.endswith(".json"):
                with open(path, "r") as json_data:
                    data_dict = json.load(json_data)
                keys = list(data_dict.keys())
                for i in keys:
                    data_dict[self.configMap_rev[i]] = data_dict.pop(i)

            self.populate_table(excel_dict=data_dict)
            self.update_static()

            return data_dict

        else:
            print(
                "Invalid file path or extension! \n Please ensure the filename ends with .csv or .xlsx"
            )
            return

    def populate_finealign(self, finealign_data, logging_data):
        self.fine_align_panel.populate_fa_settings(finealign_data)
        self.populate_det_settings(finealign_data, logging_data)

    def populate_det_settings(self, finealign_dict, det_dict):
        if finealign_dict["Optimize Wavelength"][0] == True:
            self.yes.setChecked(True)
            self.no.setChecked(False)
        else:
            self.yes.setChecked(False)
            self.no.setChecked(True)

        self.fine_interval.setText(str(int(finealign_dict["Interval"][0])))

        if finealign_dict["Use Central Wavelength"][0] == True:
            self.userWL.setChecked(False)
            self.centralWL.setChecked(True)
        else:
            self.userWL.setChecked(True)
            self.centralWL.setChecked(False)

        try:
            hp816x_list = det_dict["HP816x"][0].strip("][").split(",")
            for i in hp816x_list:
                self.hp816x_buttons[int(i) - 1].setChecked(True)

            n77_list = det_dict["N77"][0].strip("][").split(",")
            for i in n77_list:
                self.n77_buttons[int(i) - 1].setChecked(True)

        except Exception as e:
            print(
                "Some or all Detectors Logging input is invalid. Please and try again. {}".format(
                    e
                )
            )

    def export_xlsx(self):
        try:
            self.get_config()
            self.multisweep.update_config()
            self.multisweep.validate_input()

            df = pd.DataFrame(
                (
                    dict(
                        [
                            (k, pd.Series(v))
                            for k, v in self.multisweep.config["segment"].items()
                        ]
                    )
                )
            ).drop(columns=["isTime"])
            df.columns = [
                self.configMap_rev[val] for val in df.columns
            ]  # Change columns name

            df2 = pd.DataFrame(
                (
                    dict(
                        [
                            (k, pd.Series(v))
                            for k, v in self.multisweep.config["fineAlign"].items()
                        ]
                    )
                )
            )
            df2.columns = [
                self.fineAlignMap_rev[val] for val in df2.columns
            ]  # Change columns name

            df3 = pd.Series(self.multisweep.config["logging"]).to_frame().T

            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Select file to save parameters settings")
            msgBox.setStandardButtons(
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
            )
            returnValue = msgBox.exec()

            if returnValue == QtWidgets.QMessageBox.Cancel:
                return

            path = QtWidgets.QFileDialog.getSaveFileName(
                self, "Open file", self.multisweep.path[0], filter="Excel (*.xlsx)"
            )
            df.to_excel(path[0])

            msgBox.setText("Select file to save fineAlign and logging settings")
            returnValue = msgBox.exec()

            if returnValue == QtWidgets.QMessageBox.Cancel:
                return

            path = QtWidgets.QFileDialog.getSaveFileName(
                self, "Open file", path[0], "Excel (*.xlsx)"
            )

            with pd.ExcelWriter(path[0]) as writer:
                df2.to_excel(
                    writer, sheet_name="Other Configs", startrow=0, index=False
                )
                df3.to_excel(
                    writer, sheet_name="Other Configs", startrow=3, index=False
                )

            logging.info("Successfully export excel to {}".format(path[0]))

        except Exception as e:
            print(e)

    def add_row(self):
        rowPosition = self.tableWidget.currentRow()

        if rowPosition < 2:
            rowPosition = 1
        self.tableWidget.insertRow(rowPosition + 1)

        # populate new row for each column
        for i in range(self.tableWidget.columnCount()):
            header = self.tableWidget.horizontalHeaderItem(i).text()
            header = self.configMap[header]
            self.tableWidget.setItem(
                rowPosition + 1,
                i,
                QTableWidgetItem(str(self.multisweep.config["default"][header])),
            )
        self.update_row()
        self.update_finalign_wavelength()
        return rowPosition

    def duplicate_row(self):
        self.add_row()

        rowPosition = self.tableWidget.currentRow()
        columnPosition = self.tableWidget.columnCount()

        for i in range(columnPosition):
            if not self.tableWidget.item(rowPosition, i) is None:
                self.tableWidget.setItem(
                    rowPosition + 1,
                    i,
                    QtWidgets.QTableWidgetItem(
                        self.tableWidget.item(rowPosition, i).text()
                    ),
                )

        self.update_row()
        self.update_finalign_wavelength()
        return None

    def delete_row(self):
        rows = self.tableWidget.selectionModel().selectedRows()
        if self.tableWidget.rowCount() > 2 and self.tableWidget.currentRow() > 1:
            indexes = []
            for row in rows:
                indexes.append(row.row())
            # Reverse sort rows indexes
            indexes = sorted(indexes, reverse=True)

            for rowidx in indexes:
                self.tableWidget.removeRow(rowidx)

        self.update_row()
        return None

    def update_row(self):
        header = ["Static", "Logging"]
        header.extend([str(i) for i in range(1, self.tableWidget.rowCount())])
        self.tableWidget.setVerticalHeaderLabels(header)
        self.update_static()

        return None

    def populate_table(self, excel_dict=None, start_col=0, end_col=None):
        if end_col is None:
            end_col = self.tableWidget.columnCount()

        if excel_dict:
            # set row based on rows in logs
            try:
                self.tableWidget.setRowCount(
                    len(excel_dict["Start Wavelength (nm)"]) + 2
                )
            except:
                self.tableWidget.setRowCount(
                    len(excel_dict[self.configMap["Start Wavelength (nm)"]]) + 2
                )

        # populate table for each column
        for i in range(start_col, end_col):
            header = self.tableWidget.horizontalHeaderItem(i).text()
            for j in range(2, self.tableWidget.rowCount()):
                if excel_dict:
                    if header in excel_dict.keys():
                        self.tableWidget.setItem(
                            j, i, QTableWidgetItem(str(excel_dict[header][j - 2]))
                        )
                else:
                    self.tableWidget.setItem(
                        j,
                        i,
                        QTableWidgetItem(
                            str(
                                self.multisweep.config["default"][
                                    self.configMap[header]
                                ]
                            )
                        ),
                    )

        self.update_row()
        self.update_finalign_wavelength()

    def update_table(self):
        self.wavelength.setExclusive(False)
        self.userWL.setChecked(False)
        self.wavelength.setExclusive(True)

        columns = [
            "Segment Time (min)",
            "Output Path",
            "Laser Intensity (dBm)",
            "Start Wavelength (nm)",
            "End Wavelength (nm)",
            "Sweep Step (nm)",
            "Sweep Speed (nm)",
            "FineAlign Wavelength (nm)",
        ]

        if self.sweep.isChecked():
            columns[0] = "# of Sweep"

        for i in self.multisweep.confirm_instr:
            if i == "TEC1":
                columns.extend(self.instr_map["TEC"])

        # set table to the correct format
        start_col = self.tableWidget.columnCount()
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)
        self.get_static_param()
        self.populate_table(start_col=start_col)
        self.tableWidget.resizeColumnsToContents()

    def set_checked(self, column=None):
        for i in range(1, self.tableWidget.columnCount()):
            for j in range(2):
                item = QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)
                if j == 1:
                    item.setCheckState(QtCore.Qt.Checked)

                if column is None or i in column:
                    self.tableWidget.setItem(j, i, item)

    def get_config(self):
        # try:
        segment = self.multisweep.config["segment"]
        (
            segment["sweep"],
            segment["time"],
            segment["fineAlignWavelength"],
            segment["isTime"],
        ) = ([], [], [], self.time.isChecked())

        for i in range(self.tableWidget.columnCount()):
            column_name = self.tableWidget.horizontalHeaderItem(i).text()
            column_name = self.configMap[column_name]
            segment[column_name] = []

            for j in range(2, self.tableWidget.rowCount()):
                if column_name != "outputPath" and column_name != "sweepSpeed":
                    try:
                        segment[column_name].append(
                            float(self.tableWidget.item(j, i).text())
                        )

                    except Exception as e:
                        if (
                            not column_name == "fineAlignWavelength"
                            and self.centralWL.isChecked()
                        ):
                            raise ValueError(
                                "{} provided in row {} is invalid. {}. \nPlease check values and formatting before continuing.".format(
                                    self.configMap_rev[column_name], j - 1, e
                                )
                            )

                else:
                    segment[column_name].append(str(self.tableWidget.item(j, i).text()))

                if column_name == "fineAlignWavelength":
                    if self.centralWL.isChecked():
                        segment["fineAlignWavelength"].append(
                            float(
                                (
                                    segment["endWavelength"][j - 2]
                                    + segment["startWavelength"][j - 2]
                                )
                                / 2
                            )
                        )

        # get logging values
        (
            self.multisweep.config["logging"]["HP816x"],
            self.multisweep.config["logging"]["N77"],
            self.multisweep.config["logging"]["tec1"],
        ) = ([], [], [])

        for i in self.hp816x_buttons:
            if i.isChecked():
                self.multisweep.config["logging"]["HP816x"].append(int(i.text()))

        for i in self.n77_buttons:
            if i.isChecked():
                self.multisweep.config["logging"]["N77"].append(int(i.text()))

        if self.multisweep.tec1:
            for i in self.tec1_buttons.buttons():
                if i.isChecked():
                    self.multisweep.config["logging"]["tec1"].append(i.text())

        # get fine align config
        self.multisweep.config[
            "fineAlign"
        ] = self.fine_align_panel.get_fineAlign_config()
        self.multisweep.config["fineAlign"]["interval"] = int(self.fine_interval.text())
        self.multisweep.config["fineAlign"]["centralWL"] = self.centralWL.isChecked()
        self.multisweep.config["fineAlign"]["optimizeWL"] = self.yes.isChecked()

        # except Exception as e:
        #     raise ValueError(e)

    def get_static_param(self):
        static_params = []

        for i in range(1, self.tableWidget.columnCount()):
            try:
                val = self.tableWidget.item(0, i).checkState()
                if val == QtCore.Qt.CheckState.Checked:
                    static_params.append(i)
            except:
                self.set_checked(column=[i])

        return static_params

    def update_static(self, item=None):
        if item is None:
            cols = self.get_static_param()
            for col in cols:
                for i in range(3, self.tableWidget.rowCount()):
                    self.tableWidget.setItem(
                        i,
                        col,
                        QtWidgets.QTableWidgetItem(
                            self.tableWidget.item(2, col).text()
                        ),
                    )
                    self.tableWidget.item(i, col).setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
                    )
        else:
            if item.row() == 0:
                status = item.checkState()
            elif item.row() == 2:
                status = self.tableWidget.item(0, item.column()).checkState()
            else:
                return

            for i in range(3, self.tableWidget.rowCount()):
                if status == QtCore.Qt.CheckState.Checked:
                    self.tableWidget.setItem(
                        i,
                        item.column(),
                        QtWidgets.QTableWidgetItem(
                            self.tableWidget.item(2, item.column()).text()
                        ),
                    )
                    self.tableWidget.item(i, item.column()).setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
                    )
                else:
                    try:
                        self.tableWidget.item(i, item.column()).setFlags(
                            ~QtCore.Qt.ItemIsSelectable | ~QtCore.Qt.ItemIsEditable
                        )
                    except AttributeError:
                        continue


class FineAlignWindow(QtWidgets.QGroupBox, Ui_Form):
    def __init__(self, fineAlign=None):
        super(FineAlignWindow, self).__init__()
        self.setupUi(self)
        self.fineAlign = fineAlign
        self.laserOutputMap = dict([("High Power", "highpower"), ("Low SSE", "lowsse")])
        self.fineAlign = None
        self.apply.clicked.connect(self.apply_settings)
        self.fine_align_config = {}
        self.det_options = []
        self.detectors = [self.det_1, self.det_2, self.det_3, self.det_4]
        self.det_options = ["one", "two", "three", "four", "five"]
        self.detPriority = []

    def detSlot(self):
        self.det_options = []
        if self.fineAlign is not None:
            self.det_options.append("None")

            for slotInfo in self.fineAlign.laser.pwmSlotMap:
                self.det_options.append(
                    "Slot %d Det %d" % (slotInfo[0], slotInfo[1] + 1)
                )
            if self.fineAlign.laser.name == "hp816x N77 Detector":
                for slotInfo in self.fineAlign.laser.N77pwmSlotIndex:
                    self.det_options.append("N77 Det %d" % slotInfo)

            for det in self.detectors:
                val = det.currentText()
                det.clear()
                det.addItems(self.det_options)
                if val != "":
                    det.setCurrentIndex(self.det_options.index(val))

    def populate_fa_settings(self, configs):
        # print(configs)
        # det_list = configs['Detector Priority'][0].strip('][]').split(',')
        # for det, val in zip(self.detectors, configs['Detector Priority'][0].split(',')):
        #     det.setCurrentText(self.det_options[int(val)])

        self.fine_step.setText(str(configs["Step Size (nm)"][0]))
        self.fine_scan.setText(str(configs["Window Size (nm)"][0]))
        self.fine_thres.setText(str(configs["Power Threshold (dBm)"][0]))
        self.fine_power.setText(str(configs["Laser Power (dBm)"][0]))

        print("Successfully load fineAlign settings")

    def apply_settings(self):
        if self.fineAlign:
            self.detPriority = []

            for det in self.detectors:
                val = det.currentText()
                if val != "None":
                    detIndex = self.det_options.index(val)
                    self.detPriority.append(detIndex - 1)

            print("Detector Priority being use: {}".format(self.detPriority))
            self.fineAlign.detectorPriority = self.detPriority
            self.fineAlign.laserSlot = self.fine_slot.currentText()
            self.fineAlign.laserPower = float(self.fine_power.text())
            self.fineAlign.laserOutput = self.laserOutputMap[
                self.fine_output.currentText()
            ]
            self.fineAlign.stepSize = float(self.fine_step.text())
            self.fineAlign.threshold = float(self.fine_thres.text())
            self.fineAlign.scanWindowSize = float(self.fine_scan.text())

            logging.info("Successfully Apply fineAlign Settings")

        else:
            logging.info("FineAlign not initialized. Cannot apply settings")

        self.close()

    def get_fineAlign_config(self):
        self.fine_align_config["detectorPriority"] = self.detPriority
        self.fine_align_config["laserPower"] = float(self.fine_power.text())
        self.fine_align_config["stepSize"] = float(self.fine_step.text())
        self.fine_align_config["powerThreshold"] = float(self.fine_thres.text())
        self.fine_align_config["windowSize"] = float(self.fine_scan.text())

        return self.fine_align_config
