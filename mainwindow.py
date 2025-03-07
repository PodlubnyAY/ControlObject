# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCharts import QChartView
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTableView, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1070, 594)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_4 = QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.chartView1 = QChartView(self.centralwidget)
        self.chartView1.setObjectName(u"chartView1")

        self.gridLayout_3.addWidget(self.chartView1, 0, 0, 1, 1)

        self.chartView2 = QChartView(self.centralwidget)
        self.chartView2.setObjectName(u"chartView2")

        self.gridLayout_3.addWidget(self.chartView2, 1, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.btnAdd = QPushButton(self.centralwidget)
        self.btnAdd.setObjectName(u"btnAdd")

        self.gridLayout_2.addWidget(self.btnAdd, 0, 0, 1, 1)

        self.tblItems = QTableView(self.centralwidget)
        self.tblItems.setObjectName(u"tblItems")

        self.gridLayout_2.addWidget(self.tblItems, 2, 0, 1, 3)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lblStatistics = QLabel(self.groupBox)
        self.lblStatistics.setObjectName(u"lblStatistics")
        self.lblStatistics.setTextFormat(Qt.RichText)

        self.gridLayout.addWidget(self.lblStatistics, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 4, 0, 1, 3)

        self.btnRemove = QPushButton(self.centralwidget)
        self.btnRemove.setObjectName(u"btnRemove")

        self.gridLayout_2.addWidget(self.btnRemove, 0, 1, 1, 1)

        self.cmbYear = QComboBox(self.centralwidget)
        self.cmbYear.setObjectName(u"cmbYear")

        self.gridLayout_2.addWidget(self.cmbYear, 1, 2, 1, 1)

        self.btnEdit = QPushButton(self.centralwidget)
        self.btnEdit.setObjectName(u"btnEdit")

        self.gridLayout_2.addWidget(self.btnEdit, 0, 2, 1, 1)

        self.cmbRegions = QComboBox(self.centralwidget)
        self.cmbRegions.setObjectName(u"cmbRegions")

        self.gridLayout_2.addWidget(self.cmbRegions, 1, 0, 1, 2)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btnShow = QPushButton(self.groupBox_2)
        self.btnShow.setObjectName(u"btnShow")

        self.horizontalLayout_2.addWidget(self.btnShow)

        self.layoutTypes = QHBoxLayout()
        self.layoutTypes.setObjectName(u"layoutTypes")

        self.horizontalLayout_2.addLayout(self.layoutTypes)


        self.gridLayout_2.addWidget(self.groupBox_2, 3, 0, 1, 3)


        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.chartView3 = QChartView(self.centralwidget)
        self.chartView3.setObjectName(u"chartView3")

        self.gridLayout_4.addWidget(self.chartView3, 0, 2, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1070, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btnAdd.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", None))
        self.lblStatistics.setText("")
        self.btnRemove.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.btnEdit.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u0422\u0438\u043f", None))
        self.btnShow.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c", None))
    # retranslateUi

