# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_runMulti.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QLayout, QPushButton, QSizePolicy, QSpacerItem,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_GroupBox(object):
    def setupUi(self, GroupBox):
        if not GroupBox.objectName():
            GroupBox.setObjectName(u"GroupBox")
        GroupBox.resize(1141, 823)
        self.horizontalLayout_2 = QHBoxLayout(GroupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(20, 20, 20, -1)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 0, 20, -1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.label_8 = QLabel(GroupBox)
        self.label_8.setObjectName(u"label_8")
        font = QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)

        self.verticalLayout.addWidget(self.label_8)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.start = QPushButton(GroupBox)
        self.start.setObjectName(u"start")
        self.start.setMinimumSize(QSize(80, 30))

        self.horizontalLayout.addWidget(self.start)

        self.stop = QPushButton(GroupBox)
        self.stop.setObjectName(u"stop")
        self.stop.setEnabled(False)
        self.stop.setMinimumSize(QSize(80, 30))

        self.horizontalLayout.addWidget(self.stop)

        self.pause = QPushButton(GroupBox)
        self.pause.setObjectName(u"pause")
        self.pause.setEnabled(False)
        self.pause.setMinimumSize(QSize(80, 30))

        self.horizontalLayout.addWidget(self.pause)

        self.resume = QPushButton(GroupBox)
        self.resume.setObjectName(u"resume")
        self.resume.setEnabled(False)
        self.resume.setMinimumSize(QSize(80, 30))

        self.horizontalLayout.addWidget(self.resume)

        self.horizontalSpacer_2 = QSpacerItem(2, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.horizontalLayout.setStretch(4, 2)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(GroupBox)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setPointSize(11)
        self.label.setFont(font1)

        self.verticalLayout_2.addWidget(self.label)

        self.fineAlignLog = QTextBrowser(GroupBox)
        self.fineAlignLog.setObjectName(u"fineAlignLog")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fineAlignLog.sizePolicy().hasHeightForWidth())
        self.fineAlignLog.setSizePolicy(sizePolicy)
        self.fineAlignLog.setMaximumSize(QSize(500, 60))
        self.fineAlignLog.setBaseSize(QSize(20, 39))
        self.fineAlignLog.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.verticalLayout_2.addWidget(self.fineAlignLog)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.verticalLayout_3.setStretch(2, 2)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.graphLayout = QVBoxLayout()
        self.graphLayout.setObjectName(u"graphLayout")
        self.graphLayout.setContentsMargins(-1, -1, 0, -1)

        self.horizontalLayout_2.addLayout(self.graphLayout)

        self.horizontalLayout_2.setStretch(1, 2)

        self.retranslateUi(GroupBox)

        QMetaObject.connectSlotsByName(GroupBox)
    # setupUi

    def retranslateUi(self, GroupBox):
        GroupBox.setWindowTitle(QCoreApplication.translate("GroupBox", u"GroupBox", None))
        self.label_8.setText(QCoreApplication.translate("GroupBox", u"Multi-sweep:", None))
        self.start.setText(QCoreApplication.translate("GroupBox", u"Start", None))
        self.stop.setText(QCoreApplication.translate("GroupBox", u"Stop", None))
        self.pause.setText(QCoreApplication.translate("GroupBox", u"Pause", None))
        self.resume.setText(QCoreApplication.translate("GroupBox", u"Resume", None))
        self.label.setText(QCoreApplication.translate("GroupBox", u"FineAlign Status", None))
    # retranslateUi

