# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_connect_dev.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_GroupBox(object):
    def setupUi(self, GroupBox):
        if not GroupBox.objectName():
            GroupBox.setObjectName(u"GroupBox")
        GroupBox.resize(651, 569)
        GroupBox.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        GroupBox.setCheckable(False)
        self.horizontalLayout = QHBoxLayout(GroupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(GroupBox)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(460, 300))
        self.groupBox.setMaximumSize(QSize(401, 300))
        self.groupBox.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.discon_stage = QPushButton(self.groupBox)
        self.discon_stage.setObjectName(u"discon_stage")
        self.discon_stage.setEnabled(False)
        self.discon_stage.setGeometry(QRect(360, 120, 71, 21))
        self.device_3 = QComboBox(self.groupBox)
        self.device_3.addItem("")
        self.device_3.setObjectName(u"device_3")
        self.device_3.setGeometry(QRect(20, 250, 91, 21))
        self.con_dev_3 = QPushButton(self.groupBox)
        self.connect_buttons = QButtonGroup(GroupBox)
        self.connect_buttons.setObjectName(u"connect_buttons")
        self.connect_buttons.addButton(self.con_dev_3)
        self.con_dev_3.setObjectName(u"con_dev_3")
        self.con_dev_3.setGeometry(QRect(280, 250, 71, 21))
        self.discon_laser = QPushButton(self.groupBox)
        self.discon_laser.setObjectName(u"discon_laser")
        self.discon_laser.setEnabled(False)
        self.discon_laser.setGeometry(QRect(360, 50, 71, 21))
        self.address_stage = QLabel(self.groupBox)
        self.address_stage.setObjectName(u"address_stage")
        self.address_stage.setGeometry(QRect(120, 120, 141, 16))
        self.address_stage.setAutoFillBackground(False)
        self.address_stage.setStyleSheet(u"background-color: white; \n"
"")
        self.withN77 = QCheckBox(self.groupBox)
        self.withN77.setObjectName(u"withN77")
        self.withN77.setGeometry(QRect(20, 80, 81, 20))
        self.con_laser = QPushButton(self.groupBox)
        self.connect_buttons.addButton(self.con_laser)
        self.con_laser.setObjectName(u"con_laser")
        self.con_laser.setGeometry(QRect(280, 50, 71, 21))
        self.laser_text = QComboBox(self.groupBox)
        self.laser_text.addItem("")
        self.laser_text.addItem("")
        self.laser_text.addItem("")
        self.laser_text.setObjectName(u"laser_text")
        self.laser_text.setGeometry(QRect(20, 50, 91, 21))
        self.label_19 = QLabel(self.groupBox)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(20, 230, 111, 20))
        font = QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.label_19.setFont(font)
        self.address_3 = QComboBox(self.groupBox)
        self.address_3.addItem("")
        self.address_3.setObjectName(u"address_3")
        self.address_3.setGeometry(QRect(120, 250, 141, 21))
        self.device_2 = QComboBox(self.groupBox)
        self.device_2.addItem("")
        self.device_2.addItem("")
        self.device_2.addItem("")
        self.device_2.setObjectName(u"device_2")
        self.device_2.setGeometry(QRect(20, 200, 91, 21))
        self.con_dev_2 = QPushButton(self.groupBox)
        self.connect_buttons.addButton(self.con_dev_2)
        self.con_dev_2.setObjectName(u"con_dev_2")
        self.con_dev_2.setGeometry(QRect(280, 200, 71, 21))
        self.label_15 = QLabel(self.groupBox)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(20, 100, 81, 20))
        self.label_15.setFont(font)
        self.label_14 = QLabel(self.groupBox)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(20, 30, 81, 20))
        self.label_14.setFont(font)
        self.address_2 = QComboBox(self.groupBox)
        self.address_2.addItem("")
        self.address_2.setObjectName(u"address_2")
        self.address_2.setGeometry(QRect(120, 200, 141, 21))
        self.device_1 = QComboBox(self.groupBox)
        self.device_1.addItem("")
        self.device_1.addItem("")
        self.device_1.addItem("")
        self.device_1.setObjectName(u"device_1")
        self.device_1.setGeometry(QRect(20, 170, 91, 21))
        self.address_1 = QComboBox(self.groupBox)
        self.address_1.addItem("")
        self.address_1.setObjectName(u"address_1")
        self.address_1.setGeometry(QRect(120, 170, 141, 21))
        self.discon_dev_3 = QPushButton(self.groupBox)
        self.discon_dev_3.setObjectName(u"discon_dev_3")
        self.discon_dev_3.setEnabled(False)
        self.discon_dev_3.setGeometry(QRect(360, 250, 71, 21))
        self.discon_dev_2 = QPushButton(self.groupBox)
        self.discon_dev_2.setObjectName(u"discon_dev_2")
        self.discon_dev_2.setEnabled(False)
        self.discon_dev_2.setGeometry(QRect(360, 200, 71, 21))
        self.address_laser = QLabel(self.groupBox)
        self.address_laser.setObjectName(u"address_laser")
        self.address_laser.setGeometry(QRect(120, 50, 141, 16))
        self.address_laser.setAutoFillBackground(False)
        self.address_laser.setStyleSheet(u"background-color: white; \n"
"")
        self.label_18 = QLabel(self.groupBox)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(20, 150, 81, 20))
        self.label_18.setFont(font)
        self.con_dev_1 = QPushButton(self.groupBox)
        self.connect_buttons.addButton(self.con_dev_1)
        self.con_dev_1.setObjectName(u"con_dev_1")
        self.con_dev_1.setGeometry(QRect(280, 170, 71, 21))
        self.discon_dev_1 = QPushButton(self.groupBox)
        self.discon_dev_1.setObjectName(u"discon_dev_1")
        self.discon_dev_1.setEnabled(False)
        self.discon_dev_1.setGeometry(QRect(360, 170, 71, 21))
        self.con_stage = QPushButton(self.groupBox)
        self.connect_buttons.addButton(self.con_stage)
        self.con_stage.setObjectName(u"con_stage")
        self.con_stage.setGeometry(QRect(280, 120, 71, 21))
        self.stage_text = QComboBox(self.groupBox)
        self.stage_text.addItem("")
        self.stage_text.addItem("")
        self.stage_text.setObjectName(u"stage_text")
        self.stage_text.setGeometry(QRect(20, 120, 91, 21))

        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, 150, -1)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.confirm_button = QPushButton(GroupBox)
        self.confirm_button.setObjectName(u"confirm_button")

        self.horizontalLayout_2.addWidget(self.confirm_button)

        self.edit_button = QPushButton(GroupBox)
        self.edit_button.setObjectName(u"edit_button")

        self.horizontalLayout_2.addWidget(self.edit_button)

        self.horizontalLayout_2.setStretch(0, 2)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(17, 37, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout.setStretch(2, 2)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout.setStretch(1, 2)

        self.retranslateUi(GroupBox)

        QMetaObject.connectSlotsByName(GroupBox)
    # setupUi

    def retranslateUi(self, GroupBox):
        GroupBox.setWindowTitle(QCoreApplication.translate("GroupBox", u"GroupBox", None))
#if QT_CONFIG(accessibility)
        GroupBox.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        GroupBox.setTitle("")
        self.groupBox.setTitle(QCoreApplication.translate("GroupBox", u"Instruments", None))
        self.discon_stage.setText(QCoreApplication.translate("GroupBox", u"Disconnect", None))
        self.device_3.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))

        self.con_dev_3.setText(QCoreApplication.translate("GroupBox", u"Connect", None))
        self.discon_laser.setText(QCoreApplication.translate("GroupBox", u"Disconnect", None))
        self.address_stage.setText("")
        self.withN77.setText(QCoreApplication.translate("GroupBox", u"with N77", None))
        self.con_laser.setText(QCoreApplication.translate("GroupBox", u"Connect", None))
        self.laser_text.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))
        self.laser_text.setItemText(1, QCoreApplication.translate("GroupBox", u"O-Band", None))
        self.laser_text.setItemText(2, QCoreApplication.translate("GroupBox", u"C-Band", None))

        self.label_19.setText(QCoreApplication.translate("GroupBox", u"Other Instrments:", None))
        self.address_3.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))

        self.device_2.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))
        self.device_2.setItemText(1, QCoreApplication.translate("GroupBox", u"TEC1", None))
        self.device_2.setItemText(2, QCoreApplication.translate("GroupBox", u"LDC1", None))

        self.con_dev_2.setText(QCoreApplication.translate("GroupBox", u"Connect", None))
        self.label_15.setText(QCoreApplication.translate("GroupBox", u"Stage:", None))
        self.label_14.setText(QCoreApplication.translate("GroupBox", u"Laser:", None))
        self.address_2.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))

        self.device_1.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))
        self.device_1.setItemText(1, QCoreApplication.translate("GroupBox", u"TEC1", None))
        self.device_1.setItemText(2, QCoreApplication.translate("GroupBox", u"TEC1 w/ LDC", None))

        self.address_1.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))

        self.discon_dev_3.setText(QCoreApplication.translate("GroupBox", u"Disconnect", None))
        self.discon_dev_2.setText(QCoreApplication.translate("GroupBox", u"Disconnect", None))
        self.address_laser.setText("")
        self.label_18.setText(QCoreApplication.translate("GroupBox", u"TEC:", None))
        self.con_dev_1.setText(QCoreApplication.translate("GroupBox", u"Connect", None))
        self.discon_dev_1.setText(QCoreApplication.translate("GroupBox", u"Disconnect", None))
        self.con_stage.setText(QCoreApplication.translate("GroupBox", u"Connect", None))
        self.stage_text.setItemText(0, QCoreApplication.translate("GroupBox", u"Select", None))
        self.stage_text.setItemText(1, QCoreApplication.translate("GroupBox", u"Corvus Stage", None))

        self.confirm_button.setText(QCoreApplication.translate("GroupBox", u"Confirm", None))
        self.edit_button.setText(QCoreApplication.translate("GroupBox", u"Edit", None))
    # retranslateUi

