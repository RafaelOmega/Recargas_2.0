# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'relatorio_abastecimentoLQKjhQ.ui'
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
from PySide6.QtWidgets import (QApplication, QDateEdit, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Rel_Abastecimento(object):
    def setupUi(self, Rel_Abastecimento):
        if not Rel_Abastecimento.objectName():
            Rel_Abastecimento.setObjectName(u"Rel_Abastecimento")
        Rel_Abastecimento.resize(522, 136)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Rel_Abastecimento.setFont(font)
        self.horizontalLayout = QHBoxLayout(Rel_Abastecimento)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Relatorio = QFrame(Rel_Abastecimento)
        self.frm_Relatorio.setObjectName(u"frm_Relatorio")
        self.frm_Relatorio.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Relatorio.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Relatorio)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Data = QFrame(self.frm_Relatorio)
        self.frm_Data.setObjectName(u"frm_Data")
        self.frm_Data.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Data.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Data)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Data_Inicial = QLabel(self.frm_Data)
        self.lb_Data_Inicial.setObjectName(u"lb_Data_Inicial")
        self.lb_Data_Inicial.setMinimumSize(QSize(0, 30))
        self.lb_Data_Inicial.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Data_Inicial)

        self.dt_Data_Inicial = QDateEdit(self.frm_Data)
        self.dt_Data_Inicial.setObjectName(u"dt_Data_Inicial")
        self.dt_Data_Inicial.setMinimumSize(QSize(130, 30))
        self.dt_Data_Inicial.setMaximumSize(QSize(130, 30))
        self.dt_Data_Inicial.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dt_Data_Inicial)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.lb_Data_Final = QLabel(self.frm_Data)
        self.lb_Data_Final.setObjectName(u"lb_Data_Final")
        self.lb_Data_Final.setMinimumSize(QSize(0, 30))
        self.lb_Data_Final.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Data_Final)

        self.dt_Data_Final = QDateEdit(self.frm_Data)
        self.dt_Data_Final.setObjectName(u"dt_Data_Final")
        self.dt_Data_Final.setMinimumSize(QSize(130, 30))
        self.dt_Data_Final.setMaximumSize(QSize(130, 30))
        self.dt_Data_Final.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dt_Data_Final)


        self.verticalLayout.addWidget(self.frm_Data)

        self.frm_Codigo = QFrame(self.frm_Relatorio)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_PLaca = QLabel(self.frm_Codigo)
        self.lb_PLaca.setObjectName(u"lb_PLaca")
        self.lb_PLaca.setMinimumSize(QSize(0, 30))
        self.lb_PLaca.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_PLaca)

        self.txt_PLaca = QLineEdit(self.frm_Codigo)
        self.txt_PLaca.setObjectName(u"txt_PLaca")
        self.txt_PLaca.setMinimumSize(QSize(0, 30))
        self.txt_PLaca.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.txt_PLaca)

        self.bt_Pesquisar_Abastecimento = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Abastecimento.setObjectName(u"bt_Pesquisar_Abastecimento")
        self.bt_Pesquisar_Abastecimento.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Abastecimento.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisar_Abastecimento)


        self.verticalLayout.addWidget(self.frm_Codigo)

        self.frm_Botoes = QFrame(self.frm_Relatorio)
        self.frm_Botoes.setObjectName(u"frm_Botoes")
        self.frm_Botoes.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Botoes.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Botoes)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.bt_Filtrar = QPushButton(self.frm_Botoes)
        self.bt_Filtrar.setObjectName(u"bt_Filtrar")
        self.bt_Filtrar.setMinimumSize(QSize(0, 30))
        self.bt_Filtrar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Filtrar)


        self.verticalLayout.addWidget(self.frm_Botoes)


        self.horizontalLayout.addWidget(self.frm_Relatorio)


        self.retranslateUi(Rel_Abastecimento)

        QMetaObject.connectSlotsByName(Rel_Abastecimento)
    # setupUi

    def retranslateUi(self, Rel_Abastecimento):
        Rel_Abastecimento.setWindowTitle(QCoreApplication.translate("Rel_Abastecimento", u"Relat\u00f3rio de Abastecimento", None))
        self.lb_Data_Inicial.setText(QCoreApplication.translate("Rel_Abastecimento", u"Data Inicial:", None))
        self.lb_Data_Final.setText(QCoreApplication.translate("Rel_Abastecimento", u"Data Final:", None))
        self.lb_PLaca.setText(QCoreApplication.translate("Rel_Abastecimento", u"PLaca:", None))
        self.bt_Pesquisar_Abastecimento.setText(QCoreApplication.translate("Rel_Abastecimento", u"...", None))
        self.bt_Filtrar.setText(QCoreApplication.translate("Rel_Abastecimento", u"Filtrar", None))
    # retranslateUi

