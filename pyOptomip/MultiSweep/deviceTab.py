from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QTableWidgetItem
import pandas as pd
import logging

logger = logging.getLogger(__name__)
from MultiSweep.ui.multi_connect import Ui_GroupBox
from hp816x_instr import hp816x
from hp816x_N77Det_instr import hp816x_N77Det
from CorvusEco import CorvusEcoClass
from SRS_LDC501_instr import SRS_LDC501
import pyvisa as visa


class ConnectWindow(QtWidgets.QGroupBox, Ui_GroupBox):
    def __init__(self, multisweep):
        super(ConnectWindow, self).__init__()

        self.multisweep = multisweep
        self.setupUi(self)

        self.devices_buttons = [
            self.laser_text,
            self.stage_text,
            self.device_1,
            self.device_2,
            self.device_3,
        ]
        self.address = [self.address_1, self.address_2, self.address_3]

        self.populate_address()
        self.edit_button.clicked.connect(self.edit_device)
        self.con_laser.clicked.connect(self.connect_laser)
        self.con_stage.clicked.connect(self.connect_stage)
        self.con_dev_1.clicked.connect(self.connect_TEC1)
        self.con_dev_2.clicked.connect(self.connect_TEC2)
        self.discon_laser.clicked.connect(self.disconnect_laser)
        self.discon_stage.clicked.connect(self.disconnect_stage)
        self.discon_dev_1.clicked.connect(self.disconnect_TEC)
        self.discon_dev_2.clicked.connect(self.disconnect_TEC)

    def populate_address(self):
        try:
            rm = visa.ResourceManager()
            visaAddrLst = rm.list_resources()
            # visaAddrLst.insert('Select', 0)

            for add in self.address:
                add.addItems(visaAddrLst)

        except Exception as e:
            logging.info("Cannot populate VISA ports: " + str(e))

    def connect_laser(self):
        laser = self.laser_text.currentText()
        self.multisweep.is_N77 = self.withN77.isChecked()

        if laser == "O-Band":
            self.multisweep.is_OBand = True
        elif laser == "C-Band":
            self.multisweep.is_OBand = False

        if laser == "Select":
            print("Invalid Laser Name. Please try again.")
        else:
            try:
                # connect laser
                if self.withN77.isChecked():
                    self.multisweep.laser = hp816x_N77Det()
                    if self.multisweep.is_OBand:
                        self.multisweep.laser.connect(
                            "GPIB0::22::INSTR",
                            "TCPIP0::100.65.11.185::inst0::INSTR",
                            reset=0,
                            forceTrans=1,
                        )  # OBand
                    else:
                        print("CBand")
                        self.multisweep.laser.connect(
                            "GPIB0::20::INSTR",
                            "TCPIP0::100.65.11.185::inst0::INSTR",
                            reset=0,
                            forceTrans=1,
                        )  # CBand
                else:
                    self.multisweep.laser = hp816x()
                    if self.multisweep.is_OBand:
                        self.multisweep.laser.connect(
                            "GPIB0::22::INSTR", reset=0, forceTrans=1
                        )  # CBand
                    else:
                        self.multisweep.laser.connect(
                            "GPIB0::20::INSTR", reset=0, forceTrans=1
                        )  # CBand

                self.multisweep.active_instr.append(self.multisweep.laser)

                self.laser_text.setEnabled(False)
                self.laser_text.setStyleSheet("background-color: lightgreen;")
                self.discon_laser.setEnabled(True)
                self.con_laser.setEnabled(False)

            except Exception as e:
                print("Failed to connect to instrument: " + str(e))

    def disconnect_laser(self):
        try:
            self.multisweep.laser.disconnect()
            self.laser_text.setEnabled(True)
            self.laser_text.setStyleSheet("background-color: none;")
            self.discon_laser.setEnabled(False)
            self.con_laser.setEnabled(True)
            self.multisweep.active_instr.remove(self.multisweep.laser)

        except Exception as e:
            print("Failed to connect to instrument: " + str(e))

    def connect_stage(self):
        stage = self.stage_text.currentText()
        if stage == "Select":
            print("Invalid Stage Name. Please try again.")
        else:
            try:
                self.multisweep.stage = CorvusEcoClass()
                self.multisweep.stage.connect(
                    visaName="ASRL4::INSTR",
                    rm=visa.ResourceManager(),
                    Velocity=5,
                    Acceleration=500,
                    NumberOfAxis=3,
                )
                self.multisweep.active_instr.append(self.multisweep.stage)

                self.stage_text.setEnabled(False)
                self.stage_text.setStyleSheet("background-color: lightgreen;")
                self.discon_stage.setEnabled(True)
                self.con_stage.setEnabled(False)

            except Exception as e:
                logging.error("Failed to connect to instrument: " + str(e))

    def disconnect_stage(self):
        try:
            self.multisweep.stage.disconnect()
            self.stage_text.setStyleSheet("background-color: none;")
            self.stage_text.setEnabled(True)
            self.discon_stage.setEnabled(False)
            self.con_stage.setEnabled(True)
            self.multisweep.active_instr.remove(self.multisweep.stage)

        except Exception as e:
            print("Failed to connect to instrument: " + str(e))

    def connect_TEC1(self):
        try:
            if self.device_1.currentText() == "Select":
                print("Invalid Device Name. Please try again.")
            else:
                device = self.device_1.currentText()
                address = self.address_1.currentText()

                self.multisweep.tec1 = SRS_LDC501()
                if "LDC" in device:
                    self.multisweep.tec1.useLDC = True
                self.multisweep.tec1.connect(visaAddr=address)
                self.multisweep.active_instr.append(self.multisweep.tec1)
                self.discon_dev_1.setEnabled(True)
                self.con_dev_1.setEnabled(False)
                self.device_1.setStyleSheet("background-color: lightgreen;")
                self.device_1.setEnabled(False)
                logging.info(
                    "Successfully connect to the device. Address of current TEC: "
                    + address
                )

        except Exception as e:
            logging.error("Failed to connect to instrument: " + str(e))

    def connect_TEC2(self):
        if self.device_2.currentText() == "Select":
            self.con_dev_2.setEnabled(False)
            print("Invalid Device Name. Please try again.")
        else:
            device = self.device_2.currentText()
            address = self.address_2.currentText()

            self.multisweep.tec2 = SRS_LDC501()
            if "LDC" in device:
                self.multisweep.tec2.useLDC = True
            self.multisweep.tec2.connect(visaAddr=address)

            self.multisweep.active_instr.append(self.multisweep.tec2)
            self.discon_dev_2.setEnabled(False)
            self.con_dev_2.setEnabled(True)

    def disconnect_TEC(self):
        name = self.sender().objectName()

        if name == "discon_dev_1":
            self.multisweep.tec1.setTemperature(22)
            self.multisweep.tec1.disconnect()

            self.discon_dev_1.setEnabled(False)
            self.con_dev_1.setEnabled(True)
            self.device_1.setStyleSheet("background-color: none;")
            self.device_1.setEnabled(True)
            logging.info("Successfully disconnect to the device")
            self.multisweep.active_instr.remove(self.multisweep.tec1)

        if name == "discon_dev_2":
            self.multisweep.tec2.setTemperature(22)
            self.multisweep.tec2.disconnect()
            self.discon_dev_2.setEnabled(False)
            self.con_dev_2.setEnabled(True)
            self.device_2.setStyleSheet("background-color: none;")
            self.device_2.setEnabled(True)
            logging.info("Successfully disconnect to the device")
            self.multisweep.active_instr.remove(self.multisweep.tec2)

    def confirm_device(self):
        self.groupBox.setEnabled(False)
        self.edit_button.setEnabled(True)
        self.confirm_button.setEnabled(False)

        self.multisweep.confirm_instr = [
            i.currentText() for i in self.devices_buttons if i.currentText() != "Select"
        ]
        logging.info(
            "Confirm devices being used: {}.".format(self.multisweep.confirm_instr)
        )

        self.multisweep.config["device"]["isN77"] = self.multisweep.is_N77

        if self.laser_text.currentText() == "O-Band":
            self.multisweep.is_OBand = True
        else:
            self.multisweep.is_OBand = False

        return

    def edit_device(self):
        self.groupBox.setEnabled(True)
        self.edit_button.setEnabled(False)
        self.confirm_button.setEnabled(True)

        self.multisweep.confirm_instr = []

        return
