# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_finealign.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(197, 404)
        self.det_2 = QComboBox(Form)
        self.det_2.setObjectName(u"det_2")
        self.det_2.setGeometry(QRect(90, 70, 91, 16))
        self.det_1 = QComboBox(Form)
        self.det_1.setObjectName(u"det_1")
        self.det_1.setGeometry(QRect(90, 40, 91, 16))
        self.fine_power = QLineEdit(Form)
        self.fine_power.setObjectName(u"fine_power")
        self.fine_power.setGeometry(QRect(140, 220, 41, 16))
        self.fine_power.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(10, 70, 49, 16))
        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 40, 49, 16))
        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 220, 81, 16))
        self.label_12 = QLabel(Form)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 250, 81, 16))
        self.label_13 = QLabel(Form)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 160, 81, 16))
        self.label_14 = QLabel(Form)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(10, 280, 131, 16))
        self.fine_thres = QLineEdit(Form)
        self.fine_thres.setObjectName(u"fine_thres")
        self.fine_thres.setGeometry(QRect(140, 280, 41, 16))
        self.fine_thres.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.fine_step = QLineEdit(Form)
        self.fine_step.setObjectName(u"fine_step")
        self.fine_step.setGeometry(QRect(140, 250, 41, 16))
        self.fine_step.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.fine_slot = QComboBox(Form)
        self.fine_slot.addItem("")
        self.fine_slot.setObjectName(u"fine_slot")
        self.fine_slot.setGeometry(QRect(90, 160, 91, 16))
        self.fine_output = QComboBox(Form)
        self.fine_output.addItem("")
        self.fine_output.addItem("")
        self.fine_output.setObjectName(u"fine_output")
        self.fine_output.setGeometry(QRect(90, 190, 91, 16))
        self.label_15 = QLabel(Form)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(10, 190, 81, 16))
        self.apply = QPushButton(Form)
        self.apply.setObjectName(u"apply")
        self.apply.setGeometry(QRect(59, 340, 121, 24))
        self.label_16 = QLabel(Form)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(10, 10, 131, 16))
        self.label_17 = QLabel(Form)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(10, 310, 131, 16))
        self.fine_scan = QLineEdit(Form)
        self.fine_scan.setObjectName(u"fine_scan")
        self.fine_scan.setGeometry(QRect(140, 310, 41, 16))
        self.fine_scan.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.det_3 = QComboBox(Form)
        self.det_3.setObjectName(u"det_3")
        self.det_3.setGeometry(QRect(90, 100, 91, 16))
        self.label_10 = QLabel(Form)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(10, 100, 49, 16))
        self.det_4 = QComboBox(Form)
        self.det_4.setObjectName(u"det_4")
        self.det_4.setGeometry(QRect(90, 130, 91, 16))
        self.label_18 = QLabel(Form)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(10, 130, 49, 16))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.fine_power.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Priority 2", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Priority 1", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Power (dBm)", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Step size (um)", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Laser Slot", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Scan Threshold (dBm)", None))
        self.fine_thres.setText(QCoreApplication.translate("Form", u"-50", None))
        self.fine_step.setText(QCoreApplication.translate("Form", u"2", None))
        self.fine_slot.setItemText(0, QCoreApplication.translate("Form", u"auto", None))

        self.fine_output.setItemText(0, QCoreApplication.translate("Form", u"High Power", None))
        self.fine_output.setItemText(1, QCoreApplication.translate("Form", u"Low Power", None))

        self.label_15.setText(QCoreApplication.translate("Form", u"Laser Output", None))
        self.apply.setText(QCoreApplication.translate("Form", u"Apply", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"Fine Align Settings", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Scan window (um)", None))
        self.fine_scan.setText(QCoreApplication.translate("Form", u"50", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Priority 3", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"Priority 4", None))
    # retranslateUi

