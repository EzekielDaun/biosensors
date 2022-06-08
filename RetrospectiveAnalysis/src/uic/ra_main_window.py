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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDockWidget, QHBoxLayout,
    QHeaderView, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QSplitter,
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
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.treeView = QTreeView(self.splitter)
        self.treeView.setObjectName(u"treeView")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.SelectedClicked)
        self.treeView.setSortingEnabled(True)
        self.splitter.addWidget(self.treeView)
        self.plot_widget = QWidget(self.splitter)
        self.plot_widget.setObjectName(u"plot_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(3)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.plot_widget.sizePolicy().hasHeightForWidth())
        self.plot_widget.setSizePolicy(sizePolicy1)
        self.plot_widget.setAutoFillBackground(False)
        self.splitter.addWidget(self.plot_widget)
        self.right_widgets = QWidget(self.splitter)
        self.right_widgets.setObjectName(u"right_widgets")
        self.verticalLayout = QVBoxLayout(self.right_widgets)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.analyzeFileButton = QPushButton(self.right_widgets)
        self.analyzeFileButton.setObjectName(u"analyzeFileButton")

        self.verticalLayout.addWidget(self.analyzeFileButton)

        self.analyzeFolderButton = QPushButton(self.right_widgets)
        self.analyzeFolderButton.setObjectName(u"analyzeFolderButton")

        self.verticalLayout.addWidget(self.analyzeFolderButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.right_widgets)

        self.horizontalLayout_2.addWidget(self.splitter)

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

        self.horizontalLayout.addWidget(self.textBrowser)

        self.logDockWidget.setWidget(self.dockWidgetContents)
        RaMainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.logDockWidget)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)

        self.retranslateUi(RaMainWindow)
        self.actionOpen.triggered.connect(RaMainWindow.slot_open_clicked)
        self.treeView.clicked.connect(RaMainWindow.slot_file_changed)
        self.treeView.activated.connect(RaMainWindow.slot_file_changed)
        self.analyzeFileButton.clicked.connect(RaMainWindow.slot_analyze_file)
        self.analyzeFolderButton.clicked.connect(RaMainWindow.slot_analyze_folder)

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
        self.analyzeFileButton.setText(QCoreApplication.translate("RaMainWindow", u"Run script (file)", None))
        self.analyzeFolderButton.setText(QCoreApplication.translate("RaMainWindow", u"Run script (folder)", None))
        self.menuFile.setTitle(QCoreApplication.translate("RaMainWindow", u"File", None))
        self.logDockWidget.setWindowTitle(QCoreApplication.translate("RaMainWindow", u"Log", None))
    # retranslateUi

