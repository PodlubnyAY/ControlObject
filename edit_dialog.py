# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(229, 189)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 2)

        self.btnCancel = QPushButton(Dialog)
        self.btnCancel.setObjectName(u"btnCancel")

        self.gridLayout.addWidget(self.btnCancel, 6, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(46, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 6, 1, 1, 1)

        self.btnAdd = QPushButton(Dialog)
        self.btnAdd.setObjectName(u"btnAdd")

        self.gridLayout.addWidget(self.btnAdd, 6, 2, 1, 1)

        self.txtPopulation = QLineEdit(Dialog)
        self.txtPopulation.setObjectName(u"txtPopulation")

        self.gridLayout.addWidget(self.txtPopulation, 5, 0, 1, 3)

        self.txtYear = QLineEdit(Dialog)
        self.txtYear.setObjectName(u"txtYear")

        self.gridLayout.addWidget(self.txtYear, 3, 0, 1, 3)

        self.cmbRegions = QComboBox(Dialog)
        self.cmbRegions.setObjectName(u"cmbRegions")

        self.gridLayout.addWidget(self.cmbRegions, 1, 0, 1, 3)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u0420\u0435\u0433\u0438\u043e\u043d", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u0413\u043e\u0434", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0441\u0435\u043b\u0435\u043d\u0438\u0435", None))
        self.btnCancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.btnAdd.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
    # retranslateUi

