# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dashboard_refeicaoXxDurq.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Dash_Refeicao(object):
    def setupUi(self, Dash_Refeicao):
        if not Dash_Refeicao.objectName():
            Dash_Refeicao.setObjectName(u"Dash_Refeicao")
        Dash_Refeicao.resize(703, 469)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Dash_Refeicao.setFont(font)
        self.verticalLayout = QVBoxLayout(Dash_Refeicao)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.webEngineView = QWebEngineView(Dash_Refeicao)
        self.webEngineView.setObjectName(u"webEngineView")
        self.webEngineView.setUrl(QUrl(u"about:blank"))

        self.verticalLayout.addWidget(self.webEngineView)


        self.retranslateUi(Dash_Refeicao)

        QMetaObject.connectSlotsByName(Dash_Refeicao)
    # setupUi

    def retranslateUi(self, Dash_Refeicao):
        Dash_Refeicao.setWindowTitle(QCoreApplication.translate("Dash_Refeicao", u"Dashboard para Recargas Refei\u00e7\u00e3o", None))
    # retranslateUi

