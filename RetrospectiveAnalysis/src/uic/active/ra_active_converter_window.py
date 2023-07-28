# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ra_active_converter_window.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialogButtonBox, QDockWidget, QDoubleSpinBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QSplitter, QStackedWidget,
    QStatusBar, QTabWidget, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(897, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_5 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter_3 = QSplitter(self.centralwidget)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Horizontal)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.groupBox = QGroupBox(self.splitter_2)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.rawLoadPushButton = QPushButton(self.groupBox)
        self.rawLoadPushButton.setObjectName(u"rawLoadPushButton")

        self.gridLayout.addWidget(self.rawLoadPushButton, 3, 0, 1, 3)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)

        self.skipRowsSpinBox = QSpinBox(self.groupBox)
        self.skipRowsSpinBox.setObjectName(u"skipRowsSpinBox")
        self.skipRowsSpinBox.setMaximum(999999999)

        self.gridLayout.addWidget(self.skipRowsSpinBox, 0, 0, 1, 1)

        self.rawRegexLineEdit = QLineEdit(self.groupBox)
        self.rawRegexLineEdit.setObjectName(u"rawRegexLineEdit")

        self.gridLayout.addWidget(self.rawRegexLineEdit, 2, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setTextFormat(Qt.MarkdownText)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setTextInteractionFlags(Qt.TextBrowserInteraction)

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.rawRampChannelSpinBox = QSpinBox(self.groupBox)
        self.rawRampChannelSpinBox.setObjectName(u"rawRampChannelSpinBox")

        self.gridLayout.addWidget(self.rawRampChannelSpinBox, 1, 2, 1, 1)

        self.skipColumnsSpinBox = QSpinBox(self.groupBox)
        self.skipColumnsSpinBox.setObjectName(u"skipColumnsSpinBox")
        self.skipColumnsSpinBox.setMaximum(999999999)

        self.gridLayout.addWidget(self.skipColumnsSpinBox, 0, 1, 1, 2)

        self.splitter_2.addWidget(self.groupBox)
        self.groupBox_2 = QGroupBox(self.splitter_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.rawPreviewFileComboBox = QComboBox(self.groupBox_2)
        self.rawPreviewFileComboBox.setObjectName(u"rawPreviewFileComboBox")

        self.verticalLayout.addWidget(self.rawPreviewFileComboBox)

        self.rawPreviewPlotSpaceholderWidget = QWidget(self.groupBox_2)
        self.rawPreviewPlotSpaceholderWidget.setObjectName(u"rawPreviewPlotSpaceholderWidget")
        sizePolicy1.setHeightForWidth(self.rawPreviewPlotSpaceholderWidget.sizePolicy().hasHeightForWidth())
        self.rawPreviewPlotSpaceholderWidget.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.rawPreviewPlotSpaceholderWidget)

        self.splitter_2.addWidget(self.groupBox_2)
        self.groupBox_4 = QGroupBox(self.splitter_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 2, 1)

        self.rampSymmetryDoubleSpinBox = QDoubleSpinBox(self.groupBox_4)
        self.rampSymmetryDoubleSpinBox.setObjectName(u"rampSymmetryDoubleSpinBox")
        self.rampSymmetryDoubleSpinBox.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.rampSymmetryDoubleSpinBox.setMaximum(100.000000000000000)
        self.rampSymmetryDoubleSpinBox.setSingleStep(50.000000000000000)
        self.rampSymmetryDoubleSpinBox.setValue(100.000000000000000)

        self.gridLayout_2.addWidget(self.rampSymmetryDoubleSpinBox, 0, 1, 2, 2)

        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)

        self.rampVMinDoubleSpinBox = QDoubleSpinBox(self.groupBox_4)
        self.rampVMinDoubleSpinBox.setObjectName(u"rampVMinDoubleSpinBox")
        self.rampVMinDoubleSpinBox.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.rampVMinDoubleSpinBox, 2, 1, 1, 2)

        self.label_6 = QLabel(self.groupBox_4)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.label_6, 3, 0, 1, 1)

        self.rampVMaxDoubleSpinBox = QDoubleSpinBox(self.groupBox_4)
        self.rampVMaxDoubleSpinBox.setObjectName(u"rampVMaxDoubleSpinBox")
        self.rampVMaxDoubleSpinBox.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.rampVMaxDoubleSpinBox.setValue(3.000000000000000)

        self.gridLayout_2.addWidget(self.rampVMaxDoubleSpinBox, 3, 1, 1, 2)

        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 4, 0, 1, 1)

        self.rampFrequencyDoubleSpinBox = QDoubleSpinBox(self.groupBox_4)
        self.rampFrequencyDoubleSpinBox.setObjectName(u"rampFrequencyDoubleSpinBox")
        self.rampFrequencyDoubleSpinBox.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.rampFrequencyDoubleSpinBox.setDecimals(4)
        self.rampFrequencyDoubleSpinBox.setMaximum(999999.000000000000000)
        self.rampFrequencyDoubleSpinBox.setValue(10.000000000000000)

        self.gridLayout_2.addWidget(self.rampFrequencyDoubleSpinBox, 4, 1, 1, 2)

        self.splitter_2.addWidget(self.groupBox_4)
        self.groupBox_3 = QGroupBox(self.splitter_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.label_7)

        self.rawSpectrogramInterpolateSpinBox = QSpinBox(self.groupBox_3)
        self.rawSpectrogramInterpolateSpinBox.setObjectName(u"rawSpectrogramInterpolateSpinBox")
        self.rawSpectrogramInterpolateSpinBox.setMaximum(999999)
        self.rawSpectrogramInterpolateSpinBox.setValue(400)

        self.horizontalLayout_3.addWidget(self.rawSpectrogramInterpolateSpinBox)

        self.rawSpectrogramPlotPushButton = QPushButton(self.groupBox_3)
        self.rawSpectrogramPlotPushButton.setObjectName(u"rawSpectrogramPlotPushButton")
        self.rawSpectrogramPlotPushButton.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.rawSpectrogramPlotPushButton)

        self.splitter_2.addWidget(self.groupBox_3)
        self.splitter_3.addWidget(self.splitter_2)
        self.groupBox_5 = QGroupBox(self.splitter_3)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy2)
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(self.groupBox_5)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.groupBox_9 = QGroupBox(self.splitter)
        self.groupBox_9.setObjectName(u"groupBox_9")
        sizePolicy.setHeightForWidth(self.groupBox_9.sizePolicy().hasHeightForWidth())
        self.groupBox_9.setSizePolicy(sizePolicy)
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_9)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.inputRegulationComboBox = QComboBox(self.groupBox_9)
        self.inputRegulationComboBox.setObjectName(u"inputRegulationComboBox")

        self.verticalLayout_6.addWidget(self.inputRegulationComboBox)

        self.inputRegulationStackedWidget = QStackedWidget(self.groupBox_9)
        self.inputRegulationStackedWidget.setObjectName(u"inputRegulationStackedWidget")

        self.verticalLayout_6.addWidget(self.inputRegulationStackedWidget)

        self.splitter.addWidget(self.groupBox_9)
        self.conversionMethodGroupBox = QGroupBox(self.splitter)
        self.conversionMethodGroupBox.setObjectName(u"conversionMethodGroupBox")
        self.verticalLayout_2 = QVBoxLayout(self.conversionMethodGroupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.conversionMethodComboBox = QComboBox(self.conversionMethodGroupBox)
        self.conversionMethodComboBox.setObjectName(u"conversionMethodComboBox")

        self.verticalLayout_2.addWidget(self.conversionMethodComboBox)

        self.conversionMethodStackedWidget = QStackedWidget(self.conversionMethodGroupBox)
        self.conversionMethodStackedWidget.setObjectName(u"conversionMethodStackedWidget")
        sizePolicy.setHeightForWidth(self.conversionMethodStackedWidget.sizePolicy().hasHeightForWidth())
        self.conversionMethodStackedWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.conversionMethodStackedWidget)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.conversionMethodPolarityComboBox = QComboBox(self.conversionMethodGroupBox)
        self.conversionMethodPolarityComboBox.addItem("")
        self.conversionMethodPolarityComboBox.addItem("")
        self.conversionMethodPolarityComboBox.setObjectName(u"conversionMethodPolarityComboBox")

        self.horizontalLayout_4.addWidget(self.conversionMethodPolarityComboBox)

        self.conversionMethodOutputOffsetDoubleSpinBox = QDoubleSpinBox(self.conversionMethodGroupBox)
        self.conversionMethodOutputOffsetDoubleSpinBox.setObjectName(u"conversionMethodOutputOffsetDoubleSpinBox")
        self.conversionMethodOutputOffsetDoubleSpinBox.setMinimum(-999999.000000000000000)
        self.conversionMethodOutputOffsetDoubleSpinBox.setMaximum(999999.000000000000000)
        self.conversionMethodOutputOffsetDoubleSpinBox.setValue(1310.000000000000000)

        self.horizontalLayout_4.addWidget(self.conversionMethodOutputOffsetDoubleSpinBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.splitter.addWidget(self.conversionMethodGroupBox)
        self.groupBox_8 = QGroupBox(self.splitter)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_8)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_7 = QGroupBox(self.groupBox_8)
        self.groupBox_7.setObjectName(u"groupBox_7")
        sizePolicy.setHeightForWidth(self.groupBox_7.sizePolicy().hasHeightForWidth())
        self.groupBox_7.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.plotTrendlineCheckBox = QCheckBox(self.groupBox_7)
        self.plotTrendlineCheckBox.setObjectName(u"plotTrendlineCheckBox")
        self.plotTrendlineCheckBox.setChecked(True)

        self.horizontalLayout_2.addWidget(self.plotTrendlineCheckBox)

        self.plotTrendlineOrderSpinBox = QSpinBox(self.groupBox_7)
        self.plotTrendlineOrderSpinBox.setObjectName(u"plotTrendlineOrderSpinBox")

        self.horizontalLayout_2.addWidget(self.plotTrendlineOrderSpinBox)

        self.plotTrendlineOutlierRangeDoubleSpinBox = QDoubleSpinBox(self.groupBox_7)
        self.plotTrendlineOutlierRangeDoubleSpinBox.setObjectName(u"plotTrendlineOutlierRangeDoubleSpinBox")
        self.plotTrendlineOutlierRangeDoubleSpinBox.setMaximum(9999999999999.000000000000000)
        self.plotTrendlineOutlierRangeDoubleSpinBox.setValue(30.000000000000000)

        self.horizontalLayout_2.addWidget(self.plotTrendlineOutlierRangeDoubleSpinBox)

        self.plotPushButton = QPushButton(self.groupBox_7)
        self.plotPushButton.setObjectName(u"plotPushButton")
        self.plotPushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.plotPushButton)


        self.verticalLayout_3.addWidget(self.groupBox_7)

        self.plotTabWidget = QTabWidget(self.groupBox_8)
        self.plotTabWidget.setObjectName(u"plotTabWidget")
        self.plotTabWidget.setEnabled(False)

        self.verticalLayout_3.addWidget(self.plotTabWidget)

        self.splitter.addWidget(self.groupBox_8)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.label)

        self.outputPathComboBox = QComboBox(self.layoutWidget)
        self.outputPathComboBox.setObjectName(u"outputPathComboBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.outputPathComboBox.sizePolicy().hasHeightForWidth())
        self.outputPathComboBox.setSizePolicy(sizePolicy3)
        self.outputPathComboBox.setEditable(True)

        self.horizontalLayout.addWidget(self.outputPathComboBox)

        self.outputPathPushButton = QPushButton(self.layoutWidget)
        self.outputPathPushButton.setObjectName(u"outputPathPushButton")

        self.horizontalLayout.addWidget(self.outputPathPushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.horizontalLayout.addWidget(self.buttonBox)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_4.addWidget(self.splitter)

        self.splitter_3.addWidget(self.groupBox_5)

        self.verticalLayout_5.addWidget(self.splitter_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 897, 29))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_7 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.textBrowser = QTextBrowser(self.dockWidgetContents_2)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_7.addWidget(self.textBrowser)

        self.dockWidget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)

        self.retranslateUi(MainWindow)
        self.buttonBox.accepted.connect(MainWindow.slot_accept)
        self.buttonBox.rejected.connect(MainWindow.slot_reject)

        self.conversionMethodStackedWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Sweep Raw Preview Setting", None))
        self.rawLoadPushButton.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Ramp Channel:", None))
        self.skipRowsSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" rows", None))
        self.skipRowsSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u"skip ", None))
        self.rawRegexLineEdit.setText(QCoreApplication.translate("MainWindow", u".*measurement(\\d+).csv", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"[RegEx](https://saasbase.dev/tools/regex-generator): ", None))
        self.skipColumnsSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" columns", None))
        self.skipColumnsSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u"skip ", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Sweep Raw Preview", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Ramp Signal Config", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Symmetry:", None))
        self.rampSymmetryDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" %", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"V_min:", None))
        self.rampVMinDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" V", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"V_max:", None))
        self.rampVMaxDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" V", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Frequency:", None))
        self.rampFrequencyDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Spectrogram Raw Preview", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Interpolate:", None))
        self.rawSpectrogramPlotPushButton.setText(QCoreApplication.translate("MainWindow", u"Spectrogram", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Wavelength Conversion", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainWindow", u"Input Regulation", None))
        self.conversionMethodGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Convsersion Method", None))
        self.conversionMethodPolarityComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Output Polarity: -", None))
        self.conversionMethodPolarityComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Output Polarity: +", None))

        self.conversionMethodOutputOffsetDoubleSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u"Output Offset: ", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"Plot", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Plot Setting", None))
        self.plotTrendlineCheckBox.setText(QCoreApplication.translate("MainWindow", u"Trendline", None))
        self.plotTrendlineOrderSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u"Order: ", None))
        self.plotTrendlineOutlierRangeDoubleSpinBox.setPrefix(QCoreApplication.translate("MainWindow", u"Outlier Range: ", None))
        self.plotTrendlineOutlierRangeDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" pm", None))
        self.plotPushButton.setText(QCoreApplication.translate("MainWindow", u"Plot FSR", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Output Path:", None))
        self.outputPathPushButton.setText(QCoreApplication.translate("MainWindow", u"Select", None))
    # retranslateUi

