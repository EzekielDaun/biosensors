# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ra_main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDockWidget,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QSplitter,
    QStatusBar, QTextBrowser, QTreeView, QVBoxLayout,
    QWidget)

class Ui_RaMainWindow(object):
    def setupUi(self, RaMainWindow):
        if not RaMainWindow.objectName():
            RaMainWindow.setObjectName(u"RaMainWindow")
        RaMainWindow.resize(1280, 720)
        RaMainWindow.setMinimumSize(QSize(1280, 720))
        self.actionOpen = QAction(RaMainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(RaMainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(RaMainWindow)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionOp1 = QAction(RaMainWindow)
        self.actionOp1.setObjectName(u"actionOp1")
        self.actionOp1.setCheckable(True)
        self.centralwidget = QWidget(RaMainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.splitter_3 = QSplitter(self.centralwidget)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Horizontal)
        self.splitter = QSplitter(self.splitter_3)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Vertical)
        self.treeView = QTreeView(self.splitter)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy1)
        self.treeView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.SelectedClicked)
        self.treeView.setSortingEnabled(True)
        self.splitter.addWidget(self.treeView)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.analyzerSettingsGroupBox = QGroupBox(self.layoutWidget)
        self.analyzerSettingsGroupBox.setObjectName(u"analyzerSettingsGroupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.analyzerSettingsGroupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.analyzerSettingsGroupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.timeStampComboBox = QComboBox(self.analyzerSettingsGroupBox)
        self.timeStampComboBox.setObjectName(u"timeStampComboBox")
        self.timeStampComboBox.setEditable(True)

        self.gridLayout.addWidget(self.timeStampComboBox, 0, 1, 1, 1)

        self.label_3 = QLabel(self.analyzerSettingsGroupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.timeMultiplierLineEdit = QLineEdit(self.analyzerSettingsGroupBox)
        self.timeMultiplierLineEdit.setObjectName(u"timeMultiplierLineEdit")

        self.gridLayout.addWidget(self.timeMultiplierLineEdit, 1, 1, 1, 1)

        self.label_4 = QLabel(self.analyzerSettingsGroupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.wavelengthMultiplierLineEdit = QLineEdit(self.analyzerSettingsGroupBox)
        self.wavelengthMultiplierLineEdit.setObjectName(u"wavelengthMultiplierLineEdit")

        self.gridLayout.addWidget(self.wavelengthMultiplierLineEdit, 2, 1, 1, 1)

        self.label_6 = QLabel(self.analyzerSettingsGroupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)

        self.patternLineEdit = QLineEdit(self.analyzerSettingsGroupBox)
        self.patternLineEdit.setObjectName(u"patternLineEdit")

        self.gridLayout.addWidget(self.patternLineEdit, 3, 1, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_3)

        self.loadAnalyzerButton = QPushButton(self.analyzerSettingsGroupBox)
        self.loadAnalyzerButton.setObjectName(u"loadAnalyzerButton")

        self.verticalLayout_5.addWidget(self.loadAnalyzerButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)


        self.verticalLayout_2.addWidget(self.analyzerSettingsGroupBox)

        self.plotSpectrogramsGroupBox = QGroupBox(self.layoutWidget)
        self.plotSpectrogramsGroupBox.setObjectName(u"plotSpectrogramsGroupBox")
        self.horizontalLayout_3 = QHBoxLayout(self.plotSpectrogramsGroupBox)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.powerListWidget = QListWidget(self.plotSpectrogramsGroupBox)
        self.powerListWidget.setObjectName(u"powerListWidget")

        self.horizontalLayout_3.addWidget(self.powerListWidget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.plotSpectrogramsGroupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.sampleStepSpinBox = QSpinBox(self.plotSpectrogramsGroupBox)
        self.sampleStepSpinBox.setObjectName(u"sampleStepSpinBox")
        self.sampleStepSpinBox.setMinimum(1)

        self.gridLayout_2.addWidget(self.sampleStepSpinBox, 0, 1, 1, 1)

        self.label_5 = QLabel(self.plotSpectrogramsGroupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)

        self.xTicksSpinBox = QSpinBox(self.plotSpectrogramsGroupBox)
        self.xTicksSpinBox.setObjectName(u"xTicksSpinBox")
        self.xTicksSpinBox.setValue(20)

        self.gridLayout_2.addWidget(self.xTicksSpinBox, 1, 1, 1, 1)

        self.label_7 = QLabel(self.plotSpectrogramsGroupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_7, 2, 0, 1, 1)

        self.yTicksSpinBox = QSpinBox(self.plotSpectrogramsGroupBox)
        self.yTicksSpinBox.setObjectName(u"yTicksSpinBox")
        self.yTicksSpinBox.setMinimum(1)
        self.yTicksSpinBox.setValue(20)

        self.gridLayout_2.addWidget(self.yTicksSpinBox, 2, 1, 1, 1)

        self.label_8 = QLabel(self.plotSpectrogramsGroupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_8, 3, 0, 1, 1)

        self.powerUnitLineEdit = QLineEdit(self.plotSpectrogramsGroupBox)
        self.powerUnitLineEdit.setObjectName(u"powerUnitLineEdit")

        self.gridLayout_2.addWidget(self.powerUnitLineEdit, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.spectrogramButton = QPushButton(self.plotSpectrogramsGroupBox)
        self.spectrogramButton.setObjectName(u"spectrogramButton")

        self.verticalLayout.addWidget(self.spectrogramButton)


        self.horizontalLayout_3.addLayout(self.verticalLayout)


        self.verticalLayout_2.addWidget(self.plotSpectrogramsGroupBox)

        self.splitter.addWidget(self.layoutWidget)
        self.splitter_3.addWidget(self.splitter)
        self.peakTracingGroupBox = QGroupBox(self.splitter_3)
        self.peakTracingGroupBox.setObjectName(u"peakTracingGroupBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(4)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.peakTracingGroupBox.sizePolicy().hasHeightForWidth())
        self.peakTracingGroupBox.setSizePolicy(sizePolicy2)
        self.horizontalLayout_5 = QHBoxLayout(self.peakTracingGroupBox)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.splitter_2 = QSplitter(self.peakTracingGroupBox)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.layoutWidget1 = QWidget(self.splitter_2)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.gridLayout_3 = QGridLayout(self.layoutWidget1)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.peakTrackerPowerListWidget = QListWidget(self.layoutWidget1)
        self.peakTrackerPowerListWidget.setObjectName(u"peakTrackerPowerListWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.peakTrackerPowerListWidget.sizePolicy().hasHeightForWidth())
        self.peakTrackerPowerListWidget.setSizePolicy(sizePolicy3)
        self.peakTrackerPowerListWidget.setMaximumSize(QSize(16777215, 150))

        self.gridLayout_3.addWidget(self.peakTrackerPowerListWidget, 0, 0, 3, 1)

        self.trackPeakButton = QPushButton(self.layoutWidget1)
        self.trackPeakButton.setObjectName(u"trackPeakButton")

        self.gridLayout_3.addWidget(self.trackPeakButton, 0, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(118, 88, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_2, 1, 1, 1, 1)

        self.saveResultsButton = QPushButton(self.layoutWidget1)
        self.saveResultsButton.setObjectName(u"saveResultsButton")
        self.saveResultsButton.setEnabled(False)

        self.gridLayout_3.addWidget(self.saveResultsButton, 2, 1, 1, 1)

        self.splitter_2.addWidget(self.layoutWidget1)

        self.horizontalLayout_5.addWidget(self.splitter_2)

        self.splitter_3.addWidget(self.peakTracingGroupBox)

        self.horizontalLayout_4.addWidget(self.splitter_3)

        RaMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(RaMainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        RaMainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(RaMainWindow)
        self.statusbar.setObjectName(u"statusbar")
        RaMainWindow.setStatusBar(self.statusbar)
        self.logDockWidget = QDockWidget(RaMainWindow)
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
        RaMainWindow.addDockWidget(Qt.RightDockWidgetArea, self.logDockWidget)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)

        self.retranslateUi(RaMainWindow)
        self.actionOpen.triggered.connect(RaMainWindow.slot_open_clicked)
        self.treeView.clicked.connect(RaMainWindow.slot_file_changed)
        self.treeView.activated.connect(RaMainWindow.slot_file_changed)
        self.loadAnalyzerButton.clicked.connect(RaMainWindow.slot_load_analyzer)
        self.spectrogramButton.clicked.connect(RaMainWindow.slot_plot_spectrogram)
        self.trackPeakButton.clicked.connect(RaMainWindow.slot_track_peak)
        self.saveResultsButton.clicked.connect(RaMainWindow.slot_save_results)

        QMetaObject.connectSlotsByName(RaMainWindow)
    # setupUi

    def retranslateUi(self, RaMainWindow):
        RaMainWindow.setWindowTitle(QCoreApplication.translate("RaMainWindow", u"Retrospective Analysis", None))
        self.actionOpen.setText(QCoreApplication.translate("RaMainWindow", u"Open Folder", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("RaMainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("RaMainWindow", u"Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("RaMainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_as.setText(QCoreApplication.translate("RaMainWindow", u"Save as", None))
#if QT_CONFIG(shortcut)
        self.actionSave_as.setShortcut(QCoreApplication.translate("RaMainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionOp1.setText(QCoreApplication.translate("RaMainWindow", u"Op1", None))
        self.analyzerSettingsGroupBox.setTitle(QCoreApplication.translate("RaMainWindow", u"1. Analyzer Settings", None))
        self.label_2.setText(QCoreApplication.translate("RaMainWindow", u"Timestamp File/Number", None))
        self.timeStampComboBox.setCurrentText(QCoreApplication.translate("RaMainWindow", u"0.25", None))
        self.label_3.setText(QCoreApplication.translate("RaMainWindow", u"Time Multiplier (to minutes):", None))
        self.timeMultiplierLineEdit.setText(QCoreApplication.translate("RaMainWindow", u"1/60", None))
        self.label_4.setText(QCoreApplication.translate("RaMainWindow", u"Wavelength Multiplier (to nm):", None))
        self.wavelengthMultiplierLineEdit.setText(QCoreApplication.translate("RaMainWindow", u"1e9", None))
        self.label_6.setText(QCoreApplication.translate("RaMainWindow", u"Data File Pattern (RegEx):", None))
        self.patternLineEdit.setText(QCoreApplication.translate("RaMainWindow", u"r\".*sweep_(\\d+)\\.mat\"", None))
        self.loadAnalyzerButton.setText(QCoreApplication.translate("RaMainWindow", u"Load", None))
        self.plotSpectrogramsGroupBox.setTitle(QCoreApplication.translate("RaMainWindow", u"Optional. Plot Spectrograms", None))
        self.label.setText(QCoreApplication.translate("RaMainWindow", u"Sample Step:", None))
        self.label_5.setText(QCoreApplication.translate("RaMainWindow", u"X Ticks:", None))
        self.label_7.setText(QCoreApplication.translate("RaMainWindow", u"Y Ticks:", None))
        self.label_8.setText(QCoreApplication.translate("RaMainWindow", u"Power Unit:", None))
        self.powerUnitLineEdit.setText(QCoreApplication.translate("RaMainWindow", u"dBm", None))
        self.spectrogramButton.setText(QCoreApplication.translate("RaMainWindow", u"Spectrogram", None))
        self.peakTracingGroupBox.setTitle(QCoreApplication.translate("RaMainWindow", u"2. Peak Tracing", None))
        self.trackPeakButton.setText(QCoreApplication.translate("RaMainWindow", u"Start Track", None))
        self.saveResultsButton.setText(QCoreApplication.translate("RaMainWindow", u"Save Results", None))
        self.menuFile.setTitle(QCoreApplication.translate("RaMainWindow", u"File", None))
        self.logDockWidget.setWindowTitle(QCoreApplication.translate("RaMainWindow", u"Log", None))
    # retranslateUi

