# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ra_main_window_active.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDockWidget, QDoubleSpinBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSpinBox, QSplitter, QTextBrowser, QWidget)

class Ui_RaMainWindowActive(object):
    def setupUi(self, RaMainWindowActive):
        if not RaMainWindowActive.objectName():
            RaMainWindowActive.setObjectName(u"RaMainWindowActive")
        RaMainWindowActive.resize(1280, 720)
        RaMainWindowActive.setMinimumSize(QSize(1280, 720))
        self.actionOpen = QAction(RaMainWindowActive)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(RaMainWindowActive)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(RaMainWindowActive)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionOp1 = QAction(RaMainWindowActive)
        self.actionOp1.setObjectName(u"actionOp1")
        self.actionOp1.setCheckable(True)
        self.centralwidget = QWidget(RaMainWindowActive)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.rampSettingGroupBox = QGroupBox(self.splitter)
        self.rampSettingGroupBox.setObjectName(u"rampSettingGroupBox")
        self.gridLayout = QGridLayout(self.rampSettingGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.rampSettingGroupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.rampSettingDataPathComboBox = QComboBox(self.rampSettingGroupBox)
        self.rampSettingDataPathComboBox.setObjectName(u"rampSettingDataPathComboBox")

        self.gridLayout.addWidget(self.rampSettingDataPathComboBox, 0, 1, 1, 3)

        self.rampSettingDataSelectPushButton = QPushButton(self.rampSettingGroupBox)
        self.rampSettingDataSelectPushButton.setObjectName(u"rampSettingDataSelectPushButton")

        self.gridLayout.addWidget(self.rampSettingDataSelectPushButton, 0, 4, 1, 1)

        self.label_2 = QLabel(self.rampSettingGroupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 5, 1, 1)

        self.rampSettingRegExLineEdit = QLineEdit(self.rampSettingGroupBox)
        self.rampSettingRegExLineEdit.setObjectName(u"rampSettingRegExLineEdit")

        self.gridLayout.addWidget(self.rampSettingRegExLineEdit, 0, 6, 1, 4)

        self.label_3 = QLabel(self.rampSettingGroupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.rampSettingRampTypeComboBox = QComboBox(self.rampSettingGroupBox)
        self.rampSettingRampTypeComboBox.setObjectName(u"rampSettingRampTypeComboBox")

        self.gridLayout.addWidget(self.rampSettingRampTypeComboBox, 1, 1, 1, 1)

        self.label_5 = QLabel(self.rampSettingGroupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 1, 2, 1, 1)

        self.rampSettingRampFrequencyDoubleSpinBox = QDoubleSpinBox(self.rampSettingGroupBox)
        self.rampSettingRampFrequencyDoubleSpinBox.setObjectName(u"rampSettingRampFrequencyDoubleSpinBox")
        self.rampSettingRampFrequencyDoubleSpinBox.setDecimals(2)
        self.rampSettingRampFrequencyDoubleSpinBox.setSingleStep(0.100000000000000)
        self.rampSettingRampFrequencyDoubleSpinBox.setValue(10.000000000000000)

        self.gridLayout.addWidget(self.rampSettingRampFrequencyDoubleSpinBox, 1, 3, 1, 1)

        self.label_6 = QLabel(self.rampSettingGroupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 1, 4, 1, 2)

        self.rampSettingWavelengthMinDoubleSpinBox = QDoubleSpinBox(self.rampSettingGroupBox)
        self.rampSettingWavelengthMinDoubleSpinBox.setObjectName(u"rampSettingWavelengthMinDoubleSpinBox")
        self.rampSettingWavelengthMinDoubleSpinBox.setDecimals(2)
        self.rampSettingWavelengthMinDoubleSpinBox.setMaximum(2000.000000000000000)
        self.rampSettingWavelengthMinDoubleSpinBox.setSingleStep(0.100000000000000)
        self.rampSettingWavelengthMinDoubleSpinBox.setValue(1309.000000000000000)

        self.gridLayout.addWidget(self.rampSettingWavelengthMinDoubleSpinBox, 1, 6, 1, 1)

        self.rampSettingWavelengthMaxDoubleSpinBox = QDoubleSpinBox(self.rampSettingGroupBox)
        self.rampSettingWavelengthMaxDoubleSpinBox.setObjectName(u"rampSettingWavelengthMaxDoubleSpinBox")
        self.rampSettingWavelengthMaxDoubleSpinBox.setDecimals(2)
        self.rampSettingWavelengthMaxDoubleSpinBox.setMaximum(2000.000000000000000)
        self.rampSettingWavelengthMaxDoubleSpinBox.setSingleStep(0.100000000000000)
        self.rampSettingWavelengthMaxDoubleSpinBox.setValue(1310.000000000000000)

        self.gridLayout.addWidget(self.rampSettingWavelengthMaxDoubleSpinBox, 1, 7, 1, 1)

        self.label_4 = QLabel(self.rampSettingGroupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 1, 8, 1, 1)

        self.rampSettingTimeConstantDoubleSpinBox = QDoubleSpinBox(self.rampSettingGroupBox)
        self.rampSettingTimeConstantDoubleSpinBox.setObjectName(u"rampSettingTimeConstantDoubleSpinBox")
        self.rampSettingTimeConstantDoubleSpinBox.setDecimals(4)
        self.rampSettingTimeConstantDoubleSpinBox.setSingleStep(0.001000000000000)
        self.rampSettingTimeConstantDoubleSpinBox.setValue(0.020000000000000)

        self.gridLayout.addWidget(self.rampSettingTimeConstantDoubleSpinBox, 1, 9, 1, 1)

        self.rampSettingStartSpinBox = QSpinBox(self.rampSettingGroupBox)
        self.rampSettingStartSpinBox.setObjectName(u"rampSettingStartSpinBox")
        self.rampSettingStartSpinBox.setMaximum(999999999)
        self.rampSettingStartSpinBox.setSingleStep(100)

        self.gridLayout.addWidget(self.rampSettingStartSpinBox, 2, 6, 1, 1)

        self.rampSettingStopSpinBox = QSpinBox(self.rampSettingGroupBox)
        self.rampSettingStopSpinBox.setObjectName(u"rampSettingStopSpinBox")
        self.rampSettingStopSpinBox.setMinimum(1)
        self.rampSettingStopSpinBox.setMaximum(999999999)
        self.rampSettingStopSpinBox.setSingleStep(100)
        self.rampSettingStopSpinBox.setValue(100)

        self.gridLayout.addWidget(self.rampSettingStopSpinBox, 2, 7, 1, 1)

        self.rampSettingStepSpinBox = QSpinBox(self.rampSettingGroupBox)
        self.rampSettingStepSpinBox.setObjectName(u"rampSettingStepSpinBox")
        self.rampSettingStepSpinBox.setMinimum(1)
        self.rampSettingStepSpinBox.setMaximum(999999999)
        self.rampSettingStepSpinBox.setValue(1)

        self.gridLayout.addWidget(self.rampSettingStepSpinBox, 2, 8, 1, 1)

        self.rampSettingUpdatePushButton = QPushButton(self.rampSettingGroupBox)
        self.rampSettingUpdatePushButton.setObjectName(u"rampSettingUpdatePushButton")

        self.gridLayout.addWidget(self.rampSettingUpdatePushButton, 2, 9, 1, 1)

        self.rampSettingFSRPlotWidget = QWidget(self.rampSettingGroupBox)
        self.rampSettingFSRPlotWidget.setObjectName(u"rampSettingFSRPlotWidget")

        self.gridLayout.addWidget(self.rampSettingFSRPlotWidget, 3, 0, 1, 10)

        self.splitter.addWidget(self.rampSettingGroupBox)
        self.peakTrackingGroupBox = QGroupBox(self.splitter)
        self.peakTrackingGroupBox.setObjectName(u"peakTrackingGroupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.peakTrackingGroupBox.sizePolicy().hasHeightForWidth())
        self.peakTrackingGroupBox.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.peakTrackingGroupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_12 = QLabel(self.peakTrackingGroupBox)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_12, 0, 0, 1, 1)

        self.peakTrackingSweepStartSpinBox = QSpinBox(self.peakTrackingGroupBox)
        self.peakTrackingSweepStartSpinBox.setObjectName(u"peakTrackingSweepStartSpinBox")
        self.peakTrackingSweepStartSpinBox.setMinimum(0)
        self.peakTrackingSweepStartSpinBox.setMaximum(999999999)
        self.peakTrackingSweepStartSpinBox.setSingleStep(100)
        self.peakTrackingSweepStartSpinBox.setValue(0)

        self.gridLayout_2.addWidget(self.peakTrackingSweepStartSpinBox, 0, 1, 1, 1)

        self.label_13 = QLabel(self.peakTrackingGroupBox)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_13, 0, 2, 1, 1)

        self.peakTrackingSweepStopSpinBox = QSpinBox(self.peakTrackingGroupBox)
        self.peakTrackingSweepStopSpinBox.setObjectName(u"peakTrackingSweepStopSpinBox")
        self.peakTrackingSweepStopSpinBox.setMinimum(2)
        self.peakTrackingSweepStopSpinBox.setMaximum(999999999)
        self.peakTrackingSweepStopSpinBox.setSingleStep(100)
        self.peakTrackingSweepStopSpinBox.setValue(100)

        self.gridLayout_2.addWidget(self.peakTrackingSweepStopSpinBox, 0, 3, 1, 1)

        self.label_14 = QLabel(self.peakTrackingGroupBox)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_14, 0, 4, 1, 1)

        self.peakTrackingSweepStepSpinBox = QSpinBox(self.peakTrackingGroupBox)
        self.peakTrackingSweepStepSpinBox.setObjectName(u"peakTrackingSweepStepSpinBox")
        self.peakTrackingSweepStepSpinBox.setMinimum(1)
        self.peakTrackingSweepStepSpinBox.setMaximum(999999999)

        self.gridLayout_2.addWidget(self.peakTrackingSweepStepSpinBox, 0, 5, 1, 1)

        self.peakTrackingSpectrogramButton = QPushButton(self.peakTrackingGroupBox)
        self.peakTrackingSpectrogramButton.setObjectName(u"peakTrackingSpectrogramButton")

        self.gridLayout_2.addWidget(self.peakTrackingSpectrogramButton, 0, 6, 1, 1)

        self.peakTrackingTrackPeakButton = QPushButton(self.peakTrackingGroupBox)
        self.peakTrackingTrackPeakButton.setObjectName(u"peakTrackingTrackPeakButton")
        self.peakTrackingTrackPeakButton.setEnabled(False)

        self.gridLayout_2.addWidget(self.peakTrackingTrackPeakButton, 0, 7, 1, 1)

        self.label_16 = QLabel(self.peakTrackingGroupBox)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_16, 1, 0, 1, 1)

        self.peakTrackingWavelengthSampleSpinBox = QSpinBox(self.peakTrackingGroupBox)
        self.peakTrackingWavelengthSampleSpinBox.setObjectName(u"peakTrackingWavelengthSampleSpinBox")
        self.peakTrackingWavelengthSampleSpinBox.setMinimum(100)
        self.peakTrackingWavelengthSampleSpinBox.setMaximum(999999999)
        self.peakTrackingWavelengthSampleSpinBox.setSingleStep(10)
        self.peakTrackingWavelengthSampleSpinBox.setValue(400)

        self.gridLayout_2.addWidget(self.peakTrackingWavelengthSampleSpinBox, 1, 1, 1, 1)

        self.label_11 = QLabel(self.peakTrackingGroupBox)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_11, 1, 2, 1, 1)

        self.peakTrackingOutputPathComboBox = QComboBox(self.peakTrackingGroupBox)
        self.peakTrackingOutputPathComboBox.setObjectName(u"peakTrackingOutputPathComboBox")
        self.peakTrackingOutputPathComboBox.setEditable(True)

        self.gridLayout_2.addWidget(self.peakTrackingOutputPathComboBox, 1, 3, 1, 3)

        self.peakTrackingOutputPathPushButton = QPushButton(self.peakTrackingGroupBox)
        self.peakTrackingOutputPathPushButton.setObjectName(u"peakTrackingOutputPathPushButton")

        self.gridLayout_2.addWidget(self.peakTrackingOutputPathPushButton, 1, 6, 1, 1)

        self.peakTrackingSaveResultsButton = QPushButton(self.peakTrackingGroupBox)
        self.peakTrackingSaveResultsButton.setObjectName(u"peakTrackingSaveResultsButton")
        self.peakTrackingSaveResultsButton.setEnabled(False)

        self.gridLayout_2.addWidget(self.peakTrackingSaveResultsButton, 1, 7, 1, 1)

        self.peakTrackerWidget = QWidget(self.peakTrackingGroupBox)
        self.peakTrackerWidget.setObjectName(u"peakTrackerWidget")

        self.gridLayout_2.addWidget(self.peakTrackerWidget, 2, 0, 1, 8)

        self.splitter.addWidget(self.peakTrackingGroupBox)

        self.horizontalLayout_4.addWidget(self.splitter)

        RaMainWindowActive.setCentralWidget(self.centralwidget)
        self.logDockWidget = QDockWidget(RaMainWindowActive)
        self.logDockWidget.setObjectName(u"logDockWidget")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.horizontalLayout = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.textBrowser = QTextBrowser(self.dockWidgetContents)
        self.textBrowser.setObjectName(u"textBrowser")
        font = QFont()
        font.setFamilies([u"Cascadia Mono"])
        self.textBrowser.setFont(font)

        self.horizontalLayout.addWidget(self.textBrowser)

        self.logDockWidget.setWidget(self.dockWidgetContents)
        RaMainWindowActive.addDockWidget(Qt.BottomDockWidgetArea, self.logDockWidget)

        self.retranslateUi(RaMainWindowActive)
        self.rampSettingUpdatePushButton.clicked.connect(RaMainWindowActive.slot_ramp_setting_update)
        self.peakTrackingSpectrogramButton.clicked.connect(RaMainWindowActive.slot_peak_tracking_spectrogram)
        self.peakTrackingTrackPeakButton.clicked.connect(RaMainWindowActive.slot_peak_tracking_track_peak)
        self.peakTrackingSaveResultsButton.clicked.connect(RaMainWindowActive.slot_peak_tracking_save_results)

        QMetaObject.connectSlotsByName(RaMainWindowActive)
    # setupUi

    def retranslateUi(self, RaMainWindowActive):
        RaMainWindowActive.setWindowTitle(QCoreApplication.translate("RaMainWindowActive", u"Retrospective Analysis Active", None))
        self.actionOpen.setText(QCoreApplication.translate("RaMainWindowActive", u"Open Folder", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("RaMainWindowActive", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("RaMainWindowActive", u"Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("RaMainWindowActive", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_as.setText(QCoreApplication.translate("RaMainWindowActive", u"Save as", None))
#if QT_CONFIG(shortcut)
        self.actionSave_as.setShortcut(QCoreApplication.translate("RaMainWindowActive", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionOp1.setText(QCoreApplication.translate("RaMainWindowActive", u"Op1", None))
        self.rampSettingGroupBox.setTitle(QCoreApplication.translate("RaMainWindowActive", u"1. Ramp Setting", None))
        self.label.setText(QCoreApplication.translate("RaMainWindowActive", u"Data Path:", None))
        self.rampSettingDataSelectPushButton.setText(QCoreApplication.translate("RaMainWindowActive", u"Select...", None))
        self.label_2.setText(QCoreApplication.translate("RaMainWindowActive", u"RegEx:", None))
        self.rampSettingRegExLineEdit.setText(QCoreApplication.translate("RaMainWindowActive", u".*measurement(\\d+).*.csv", None))
        self.label_3.setText(QCoreApplication.translate("RaMainWindowActive", u"Ramp Type:", None))
        self.label_5.setText(QCoreApplication.translate("RaMainWindowActive", u"Ramp Frequency:", None))
        self.rampSettingRampFrequencyDoubleSpinBox.setSuffix(QCoreApplication.translate("RaMainWindowActive", u" Hz", None))
        self.label_6.setText(QCoreApplication.translate("RaMainWindowActive", u"Wavelength Range:", None))
        self.rampSettingWavelengthMinDoubleSpinBox.setSuffix(QCoreApplication.translate("RaMainWindowActive", u" nm", None))
        self.rampSettingWavelengthMaxDoubleSpinBox.setSuffix(QCoreApplication.translate("RaMainWindowActive", u" nm", None))
        self.label_4.setText(QCoreApplication.translate("RaMainWindowActive", u"Time Constant:", None))
        self.rampSettingTimeConstantDoubleSpinBox.setSuffix(QCoreApplication.translate("RaMainWindowActive", u" s", None))
        self.rampSettingStartSpinBox.setPrefix(QCoreApplication.translate("RaMainWindowActive", u"From: ", None))
        self.rampSettingStopSpinBox.setPrefix(QCoreApplication.translate("RaMainWindowActive", u"to: ", None))
        self.rampSettingStepSpinBox.setPrefix(QCoreApplication.translate("RaMainWindowActive", u"step: ", None))
        self.rampSettingUpdatePushButton.setText(QCoreApplication.translate("RaMainWindowActive", u"Update", None))
        self.peakTrackingGroupBox.setTitle(QCoreApplication.translate("RaMainWindowActive", u"2. Peak Tracking", None))
        self.label_12.setText(QCoreApplication.translate("RaMainWindowActive", u"Sweep From:", None))
        self.label_13.setText(QCoreApplication.translate("RaMainWindowActive", u"To:", None))
        self.label_14.setText(QCoreApplication.translate("RaMainWindowActive", u"Step:", None))
        self.peakTrackingSpectrogramButton.setText(QCoreApplication.translate("RaMainWindowActive", u"Plot Spectrogram", None))
        self.peakTrackingTrackPeakButton.setText(QCoreApplication.translate("RaMainWindowActive", u"Track Peak", None))
        self.label_16.setText(QCoreApplication.translate("RaMainWindowActive", u"Wavelength Sample:", None))
        self.peakTrackingWavelengthSampleSpinBox.setPrefix(QCoreApplication.translate("RaMainWindowActive", u"#", None))
        self.label_11.setText(QCoreApplication.translate("RaMainWindowActive", u"Output Path:", None))
#if QT_CONFIG(tooltip)
        self.peakTrackingOutputPathComboBox.setToolTip(QCoreApplication.translate("RaMainWindowActive", u"where the output .mat files should be saved", None))
#endif // QT_CONFIG(tooltip)
        self.peakTrackingOutputPathPushButton.setText(QCoreApplication.translate("RaMainWindowActive", u"Select...", None))
        self.peakTrackingSaveResultsButton.setText(QCoreApplication.translate("RaMainWindowActive", u"Save Result", None))
        self.logDockWidget.setWindowTitle(QCoreApplication.translate("RaMainWindowActive", u"Log", None))
    # retranslateUi

