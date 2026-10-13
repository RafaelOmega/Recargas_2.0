# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'lancamento_recargasZlPvur.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTableView, QVBoxLayout, QWidget)

class Ui_Lancamento_Recargas(object):
    def setupUi(self, Lancamento_Recargas):
        if not Lancamento_Recargas.objectName():
            Lancamento_Recargas.setObjectName(u"Lancamento_Recargas")
        Lancamento_Recargas.resize(819, 550)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Lancamento_Recargas.setFont(font)
        self.verticalLayout = QVBoxLayout(Lancamento_Recargas)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Cadastro = QFrame(Lancamento_Recargas)
        self.frm_Cadastro.setObjectName(u"frm_Cadastro")
        self.frm_Cadastro.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Cadastro.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_Cadastro)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.lb_Recargas = QLabel(self.frm_Cadastro)
        self.lb_Recargas.setObjectName(u"lb_Recargas")
        self.lb_Recargas.setMinimumSize(QSize(0, 30))
        self.lb_Recargas.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Recargas)

        self.txt_Recargas = QLineEdit(self.frm_Cadastro)
        self.txt_Recargas.setObjectName(u"txt_Recargas")
        self.txt_Recargas.setMinimumSize(QSize(100, 30))
        self.txt_Recargas.setMaximumSize(QSize(100, 30))

        self.horizontalLayout.addWidget(self.txt_Recargas)

        self.bt_Pesquisar_Recargas = QPushButton(self.frm_Cadastro)
        self.bt_Pesquisar_Recargas.setObjectName(u"bt_Pesquisar_Recargas")
        self.bt_Pesquisar_Recargas.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Recargas.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Pesquisar_Recargas)

        self.bt_Novo = QPushButton(self.frm_Cadastro)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(290, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frm_Cadastro)

        self.frm_Abrir_Recargas = QFrame(Lancamento_Recargas)
        self.frm_Abrir_Recargas.setObjectName(u"frm_Abrir_Recargas")
        self.frm_Abrir_Recargas.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Abrir_Recargas.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Abrir_Recargas)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Data = QLabel(self.frm_Abrir_Recargas)
        self.lb_Data.setObjectName(u"lb_Data")

        self.horizontalLayout_2.addWidget(self.lb_Data)

        self.dt_Data = QDateEdit(self.frm_Abrir_Recargas)
        self.dt_Data.setObjectName(u"dt_Data")
        self.dt_Data.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dt_Data)

        self.bt_Abrir_Recargas = QPushButton(self.frm_Abrir_Recargas)
        self.bt_Abrir_Recargas.setObjectName(u"bt_Abrir_Recargas")

        self.horizontalLayout_2.addWidget(self.bt_Abrir_Recargas)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout.addWidget(self.frm_Abrir_Recargas)

        self.frm_Inclusao_Itens = QFrame(Lancamento_Recargas)
        self.frm_Inclusao_Itens.setObjectName(u"frm_Inclusao_Itens")
        self.frm_Inclusao_Itens.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Inclusao_Itens.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frm_Inclusao_Itens)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.txt_Sem_Carga = QLineEdit(self.frm_Inclusao_Itens)
        self.txt_Sem_Carga.setObjectName(u"txt_Sem_Carga")
        self.txt_Sem_Carga.setMinimumSize(QSize(200, 30))
        self.txt_Sem_Carga.setMaximumSize(QSize(200, 30))

        self.gridLayout.addWidget(self.txt_Sem_Carga, 1, 6, 1, 1)

        self.lb_Sem_Carga = QLabel(self.frm_Inclusao_Itens)
        self.lb_Sem_Carga.setObjectName(u"lb_Sem_Carga")
        self.lb_Sem_Carga.setMinimumSize(QSize(0, 30))
        self.lb_Sem_Carga.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Sem_Carga, 1, 5, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.lb_Valor = QLabel(self.frm_Inclusao_Itens)
        self.lb_Valor.setObjectName(u"lb_Valor")
        self.lb_Valor.setMinimumSize(QSize(0, 30))
        self.lb_Valor.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Valor, 1, 7, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.txt_Carga = QLineEdit(self.frm_Inclusao_Itens)
        self.txt_Carga.setObjectName(u"txt_Carga")
        self.txt_Carga.setMinimumSize(QSize(80, 30))
        self.txt_Carga.setMaximumSize(QSize(80, 30))

        self.gridLayout.addWidget(self.txt_Carga, 1, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 10, 1, 1)

        self.dbs_Valor = QDoubleSpinBox(self.frm_Inclusao_Itens)
        self.dbs_Valor.setObjectName(u"dbs_Valor")

        self.gridLayout.addWidget(self.dbs_Valor, 1, 8, 1, 1)

        self.lb_Colaboradores = QLabel(self.frm_Inclusao_Itens)
        self.lb_Colaboradores.setObjectName(u"lb_Colaboradores")
        self.lb_Colaboradores.setMinimumSize(QSize(0, 30))
        self.lb_Colaboradores.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Colaboradores, 0, 0, 1, 1)

        self.lb_Carga = QLabel(self.frm_Inclusao_Itens)
        self.lb_Carga.setObjectName(u"lb_Carga")
        self.lb_Carga.setMinimumSize(QSize(0, 30))
        self.lb_Carga.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Carga, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.cmb_Colaboradores = QComboBox(self.frm_Inclusao_Itens)
        self.cmb_Colaboradores.setObjectName(u"cmb_Colaboradores")

        self.gridLayout.addWidget(self.cmb_Colaboradores, 0, 1, 1, 6)

        self.bt_Confirmar_Item = QPushButton(self.frm_Inclusao_Itens)
        self.bt_Confirmar_Item.setObjectName(u"bt_Confirmar_Item")

        self.gridLayout.addWidget(self.bt_Confirmar_Item, 1, 9, 1, 1)


        self.verticalLayout.addWidget(self.frm_Inclusao_Itens)

        self.frm_Itens = QFrame(Lancamento_Recargas)
        self.frm_Itens.setObjectName(u"frm_Itens")
        self.frm_Itens.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Itens.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Itens)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.tb_Itens = QTableView(self.frm_Itens)
        self.tb_Itens.setObjectName(u"tb_Itens")

        self.verticalLayout_2.addWidget(self.tb_Itens)

        self.frm_Total = QFrame(self.frm_Itens)
        self.frm_Total.setObjectName(u"frm_Total")
        self.frm_Total.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Total.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frm_Total)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(5, 5, 5, 5)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)

        self.lb_Total = QLabel(self.frm_Total)
        self.lb_Total.setObjectName(u"lb_Total")
        self.lb_Total.setMinimumSize(QSize(0, 30))
        self.lb_Total.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.lb_Total)

        self.txt_Total = QLineEdit(self.frm_Total)
        self.txt_Total.setObjectName(u"txt_Total")
        self.txt_Total.setMinimumSize(QSize(150, 30))
        self.txt_Total.setMaximumSize(QSize(150, 30))

        self.horizontalLayout_5.addWidget(self.txt_Total)


        self.verticalLayout_2.addWidget(self.frm_Total)

        self.frm_Crud_Item = QFrame(self.frm_Itens)
        self.frm_Crud_Item.setObjectName(u"frm_Crud_Item")
        self.frm_Crud_Item.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud_Item.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Crud_Item)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.bt_Limpar_Item = QPushButton(self.frm_Crud_Item)
        self.bt_Limpar_Item.setObjectName(u"bt_Limpar_Item")

        self.horizontalLayout_4.addWidget(self.bt_Limpar_Item)

        self.bt_Excluir_Item = QPushButton(self.frm_Crud_Item)
        self.bt_Excluir_Item.setObjectName(u"bt_Excluir_Item")

        self.horizontalLayout_4.addWidget(self.bt_Excluir_Item)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.bt_Sair_Recarga = QPushButton(self.frm_Crud_Item)
        self.bt_Sair_Recarga.setObjectName(u"bt_Sair_Recarga")

        self.horizontalLayout_4.addWidget(self.bt_Sair_Recarga)


        self.verticalLayout_2.addWidget(self.frm_Crud_Item)


        self.verticalLayout.addWidget(self.frm_Itens)

        self.frm_Crud = QFrame(Lancamento_Recargas)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.bt_Editar)

        self.horizontalSpacer_3 = QSpacerItem(448, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.bt_Excluir)


        self.verticalLayout.addWidget(self.frm_Crud)


        self.retranslateUi(Lancamento_Recargas)

        QMetaObject.connectSlotsByName(Lancamento_Recargas)
    # setupUi

    def retranslateUi(self, Lancamento_Recargas):
        Lancamento_Recargas.setWindowTitle(QCoreApplication.translate("Lancamento_Recargas", u"Lan\u00e7amento de Recargas", None))
        self.lb_Recargas.setText(QCoreApplication.translate("Lancamento_Recargas", u"Recargas:", None))
        self.bt_Pesquisar_Recargas.setText(QCoreApplication.translate("Lancamento_Recargas", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Lancamento_Recargas", u"+", None))
        self.lb_Data.setText(QCoreApplication.translate("Lancamento_Recargas", u"Data:", None))
        self.bt_Abrir_Recargas.setText(QCoreApplication.translate("Lancamento_Recargas", u"Abrir Recarga", None))
        self.lb_Sem_Carga.setText(QCoreApplication.translate("Lancamento_Recargas", u"Sem Carga:", None))
        self.lb_Valor.setText(QCoreApplication.translate("Lancamento_Recargas", u"Valor:", None))
        self.dbs_Valor.setPrefix(QCoreApplication.translate("Lancamento_Recargas", u"R$ ", None))
        self.lb_Colaboradores.setText(QCoreApplication.translate("Lancamento_Recargas", u"Colaboradores:", None))
        self.lb_Carga.setText(QCoreApplication.translate("Lancamento_Recargas", u"Carga:", None))
        self.bt_Confirmar_Item.setText(QCoreApplication.translate("Lancamento_Recargas", u"Confirmar", None))
        self.lb_Total.setText(QCoreApplication.translate("Lancamento_Recargas", u"Total:", None))
        self.bt_Limpar_Item.setText(QCoreApplication.translate("Lancamento_Recargas", u"Limpar", None))
        self.bt_Excluir_Item.setText(QCoreApplication.translate("Lancamento_Recargas", u"Excluir", None))
        self.bt_Sair_Recarga.setText(QCoreApplication.translate("Lancamento_Recargas", u"Sair Recarga", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Lancamento_Recargas", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Lancamento_Recargas", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Lancamento_Recargas", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Lancamento_Recargas", u"Excluir", None))
    # retranslateUi

