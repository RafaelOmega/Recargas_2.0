# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cad_saldo_contawyDODk.ui'
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

class Ui_Cad_Saldo_Conta(object):
    def setupUi(self, Cad_Saldo_Conta):
        if not Cad_Saldo_Conta.objectName():
            Cad_Saldo_Conta.setObjectName(u"Cad_Saldo_Conta")
        Cad_Saldo_Conta.resize(441, 136)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Cad_Saldo_Conta.setFont(font)
        self.horizontalLayout = QHBoxLayout(Cad_Saldo_Conta)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Cadastro = QFrame(Cad_Saldo_Conta)
        self.frm_Cadastro.setObjectName(u"frm_Cadastro")
        self.frm_Cadastro.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Cadastro.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Cadastro)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Codigo = QFrame(self.frm_Cadastro)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Codigo = QLabel(self.frm_Codigo)
        self.lb_Codigo.setObjectName(u"lb_Codigo")
        self.lb_Codigo.setMinimumSize(QSize(0, 30))
        self.lb_Codigo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Codigo)

        self.txt_Codigo = QLineEdit(self.frm_Codigo)
        self.txt_Codigo.setObjectName(u"txt_Codigo")
        self.txt_Codigo.setMinimumSize(QSize(100, 30))
        self.txt_Codigo.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_2.addWidget(self.txt_Codigo)

        self.bt_Pesquisar_Saldo_Conta = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Saldo_Conta.setObjectName(u"bt_Pesquisar_Saldo_Conta")
        self.bt_Pesquisar_Saldo_Conta.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Saldo_Conta.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisar_Saldo_Conta)

        self.bt_Novo = QPushButton(self.frm_Codigo)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frm_Codigo)

        self.frm_Corpo = QFrame(self.frm_Cadastro)
        self.frm_Corpo.setObjectName(u"frm_Corpo")
        self.frm_Corpo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Corpo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Corpo)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Data = QLabel(self.frm_Corpo)
        self.lb_Data.setObjectName(u"lb_Data")
        self.lb_Data.setMinimumSize(QSize(0, 30))
        self.lb_Data.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Data)

        self.dt_Data = QDateEdit(self.frm_Corpo)
        self.dt_Data.setObjectName(u"dt_Data")
        self.dt_Data.setMinimumSize(QSize(0, 30))
        self.dt_Data.setMaximumSize(QSize(16777215, 30))
        self.dt_Data.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dt_Data)

        self.lb_Valor = QLabel(self.frm_Corpo)
        self.lb_Valor.setObjectName(u"lb_Valor")
        self.lb_Valor.setMinimumSize(QSize(0, 30))
        self.lb_Valor.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Valor)

        self.txt_Valor = QLineEdit(self.frm_Corpo)
        self.txt_Valor.setObjectName(u"txt_Valor")
        self.txt_Valor.setMinimumSize(QSize(0, 30))
        self.txt_Valor.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.txt_Valor)


        self.verticalLayout.addWidget(self.frm_Corpo)

        self.frm_Crud = QFrame(self.frm_Cadastro)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Editar)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Excluir)


        self.verticalLayout.addWidget(self.frm_Crud)


        self.horizontalLayout.addWidget(self.frm_Cadastro)


        self.retranslateUi(Cad_Saldo_Conta)

        QMetaObject.connectSlotsByName(Cad_Saldo_Conta)
    # setupUi

    def retranslateUi(self, Cad_Saldo_Conta):
        Cad_Saldo_Conta.setWindowTitle(QCoreApplication.translate("Cad_Saldo_Conta", u"Cadastro de Saldo Conta Biz", None))
        self.lb_Codigo.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"C\u00f3digo:", None))
        self.bt_Pesquisar_Saldo_Conta.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"+", None))
        self.lb_Data.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"Data:", None))
        self.lb_Valor.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"Valor:", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Cad_Saldo_Conta", u"Excluir", None))
    # retranslateUi

