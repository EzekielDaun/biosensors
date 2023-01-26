# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ra_peak_tracker_tab_setting_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpinBox, QSplitter,
    QWidget)

class Ui_PeakTrackerTabSettingWidget(object):
    def setupUi(self, PeakTrackerTabSettingWidget):
        if not PeakTrackerTabSettingWidget.objectName():
            PeakTrackerTabSettingWidget.setObjectName(u"PeakTrackerTabSettingWidget")
        PeakTrackerTabSettingWidget.resize(1018, 109)
        self.horizontalLayout_4 = QHBoxLayout(PeakTrackerTabSettingWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.splitter = QSplitter(PeakTrackerTabSettingWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(self.layoutWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox = QComboBox(self.groupBox)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)

        self.FSROffsetLabel = QLabel(self.groupBox)
        self.FSROffsetLabel.setObjectName(u"FSROffsetLabel")
        self.FSROffsetLabel.setMaximumSize(QSize(60, 16777215))
        self.FSROffsetLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.FSROffsetLabel)

        self.spinBox = QSpinBox(self.groupBox)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setAlignment(Qt.AlignCenter)
        self.spinBox.setMinimum(-99)

        self.horizontalLayout.addWidget(self.spinBox)

        self.label_1 = QLabel(self.groupBox)
        self.label_1.setObjectName(u"label_1")
        self.label_1.setMaximumSize(QSize(10, 16777215))
        self.label_1.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.label_1)

        self.doubleSpinBox = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setDecimals(10)
        self.doubleSpinBox.setMinimum(-99.989999999999995)
        self.doubleSpinBox.setSingleStep(0.010000000000000)

        self.horizontalLayout.addWidget(self.doubleSpinBox)


        self.horizontalLayout_3.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.layoutWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.plotPeakOffsetButton = QPushButton(self.groupBox_2)
        self.plotPeakOffsetButton.setObjectName(u"plotPeakOffsetButton")

        self.gridLayout.addWidget(self.plotPeakOffsetButton, 1, 0, 1, 1)

        self.plotOverlayButton = QPushButton(self.groupBox_2)
        self.plotOverlayButton.setObjectName(u"plotOverlayButton")

        self.gridLayout.addWidget(self.plotOverlayButton, 1, 1, 1, 1)

        self.plotOffsetSpectrogramButton = QPushButton(self.groupBox_2)
        self.plotOffsetSpectrogramButton.setObjectName(u"plotOffsetSpectrogramButton")

        self.gridLayout.addWidget(self.plotOffsetSpectrogramButton, 2, 0, 1, 1)

        self.autoSaveCheckBox = QCheckBox(self.groupBox_2)
        self.autoSaveCheckBox.setObjectName(u"autoSaveCheckBox")

        self.gridLayout.addWidget(self.autoSaveCheckBox, 2, 1, 1, 1)


        self.horizontalLayout_3.addWidget(self.groupBox_2)

        self.splitter.addWidget(self.layoutWidget)

        self.horizontalLayout_4.addWidget(self.splitter)


        self.retranslateUi(PeakTrackerTabSettingWidget)

        QMetaObject.connectSlotsByName(PeakTrackerTabSettingWidget)
    # setupUi

    def retranslateUi(self, PeakTrackerTabSettingWidget):
        PeakTrackerTabSettingWidget.setWindowTitle(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Adjust", None))
        self.FSROffsetLabel.setText(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Offset = ", None))
        self.label_1.setText(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"+", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Plot", None))
        self.plotPeakOffsetButton.setText(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Peak Offset", None))
        self.plotOverlayButton.setText(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Overlay", None))
        self.plotOffsetSpectrogramButton.setText(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Offset+Spectrogram", None))
        self.autoSaveCheckBox.setText(QCoreApplication.translate("PeakTrackerTabSettingWidget", u"Auto-Save", None))
    # retranslateUi

