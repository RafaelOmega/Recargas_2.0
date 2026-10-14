# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'relatorio_recarga_colaboradoriKWOUk.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Rel_Recarga_Colaborador(object):
    def setupUi(self, Rel_Recarga_Colaborador):
        if not Rel_Recarga_Colaborador.objectName():
            Rel_Recarga_Colaborador.setObjectName(u"Rel_Recarga_Colaborador")
        Rel_Recarga_Colaborador.resize(495, 92)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Rel_Recarga_Colaborador.setFont(font)
        self.horizontalLayout = QHBoxLayout(Rel_Recarga_Colaborador)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Relatorio = QFrame(Rel_Recarga_Colaborador)
        self.frm_Relatorio.setObjectName(u"frm_Relatorio")
        self.frm_Relatorio.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Relatorio.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Relatorio)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Codigo = QFrame(self.frm_Relatorio)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Colaborador = QLabel(self.frm_Codigo)
        self.lb_Colaborador.setObjectName(u"lb_Colaborador")
        self.lb_Colaborador.setMinimumSize(QSize(0, 30))
        self.lb_Colaborador.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Colaborador)

        self.txt_Colaborador = QLineEdit(self.frm_Codigo)
        self.txt_Colaborador.setObjectName(u"txt_Colaborador")
        self.txt_Colaborador.setMinimumSize(QSize(0, 30))
        self.txt_Colaborador.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.txt_Colaborador)

        self.bt_Pesquisar_Colaborador = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Colaborador.setObjectName(u"bt_Pesquisar_Colaborador")
        self.bt_Pesquisar_Colaborador.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Colaborador.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisar_Colaborador)


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


        self.retranslateUi(Rel_Recarga_Colaborador)

        QMetaObject.connectSlotsByName(Rel_Recarga_Colaborador)
    # setupUi

    def retranslateUi(self, Rel_Recarga_Colaborador):
        Rel_Recarga_Colaborador.setWindowTitle(QCoreApplication.translate("Rel_Recarga_Colaborador", u"Relat\u00f3rio de Recargas por Colaborador", None))
        self.lb_Colaborador.setText(QCoreApplication.translate("Rel_Recarga_Colaborador", u"Colaborador:", None))
        self.bt_Pesquisar_Colaborador.setText(QCoreApplication.translate("Rel_Recarga_Colaborador", u"...", None))
        self.bt_Filtrar.setText(QCoreApplication.translate("Rel_Recarga_Colaborador", u"Filtrar", None))
    # retranslateUi

