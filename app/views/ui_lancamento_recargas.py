# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'lancamento_recargasanhqOR.ui'
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
from PySide6.QtWidgets import (QApplication, QDateEdit, QDoubleSpinBox, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableView, QVBoxLayout, QWidget)

class Ui_Lancamento_Recargas(object):
    def setupUi(self, Lancamento_Recargas):
        if not Lancamento_Recargas.objectName():
            Lancamento_Recargas.setObjectName(u"Lancamento_Recargas")
        Lancamento_Recargas.resize(1180, 545)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Lancamento_Recargas.setFont(font)
        self.verticalLayout = QVBoxLayout(Lancamento_Recargas)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.gb_Identificacao = QGroupBox(Lancamento_Recargas)
        self.gb_Identificacao.setObjectName(u"gb_Identificacao")
        self.horizontalLayout_8 = QHBoxLayout(self.gb_Identificacao)
        self.horizontalLayout_8.setSpacing(5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(5, 5, 5, 5)
        self.lb_Recargas = QLabel(self.gb_Identificacao)
        self.lb_Recargas.setObjectName(u"lb_Recargas")
        self.lb_Recargas.setMinimumSize(QSize(0, 30))
        self.lb_Recargas.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.lb_Recargas)

        self.txt_Recargas = QLineEdit(self.gb_Identificacao)
        self.txt_Recargas.setObjectName(u"txt_Recargas")
        self.txt_Recargas.setMinimumSize(QSize(100, 30))
        self.txt_Recargas.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_8.addWidget(self.txt_Recargas)

        self.bt_Pesquisar_Recargas = QPushButton(self.gb_Identificacao)
        self.bt_Pesquisar_Recargas.setObjectName(u"bt_Pesquisar_Recargas")
        self.bt_Pesquisar_Recargas.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Recargas.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_8.addWidget(self.bt_Pesquisar_Recargas)

        self.bt_Novo = QPushButton(self.gb_Identificacao)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_8.addWidget(self.bt_Novo)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.lb_Data = QLabel(self.gb_Identificacao)
        self.lb_Data.setObjectName(u"lb_Data")
        self.lb_Data.setMinimumSize(QSize(0, 30))
        self.lb_Data.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.lb_Data)

        self.dt_Data = QDateEdit(self.gb_Identificacao)
        self.dt_Data.setObjectName(u"dt_Data")
        self.dt_Data.setMinimumSize(QSize(150, 30))
        self.dt_Data.setMaximumSize(QSize(150, 30))
        self.dt_Data.setCalendarPopup(True)

        self.horizontalLayout_8.addWidget(self.dt_Data)

        self.bt_Abrir_Recargas = QPushButton(self.gb_Identificacao)
        self.bt_Abrir_Recargas.setObjectName(u"bt_Abrir_Recargas")
        self.bt_Abrir_Recargas.setMinimumSize(QSize(0, 30))
        self.bt_Abrir_Recargas.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.bt_Abrir_Recargas)


        self.verticalLayout.addWidget(self.gb_Identificacao)

        self.gb_Itens_Recarga = QGroupBox(Lancamento_Recargas)
        self.gb_Itens_Recarga.setObjectName(u"gb_Itens_Recarga")
        self.verticalLayout_4 = QVBoxLayout(self.gb_Itens_Recarga)
        self.verticalLayout_4.setSpacing(5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lb_Colaboradores = QLabel(self.gb_Itens_Recarga)
        self.lb_Colaboradores.setObjectName(u"lb_Colaboradores")
        self.lb_Colaboradores.setMinimumSize(QSize(0, 30))
        self.lb_Colaboradores.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Colaboradores)

        self.txt_Cod_Colaborador = QLineEdit(self.gb_Itens_Recarga)
        self.txt_Cod_Colaborador.setObjectName(u"txt_Cod_Colaborador")
        self.txt_Cod_Colaborador.setMinimumSize(QSize(100, 30))
        self.txt_Cod_Colaborador.setMaximumSize(QSize(100, 30))

        self.horizontalLayout.addWidget(self.txt_Cod_Colaborador)

        self.bt_Pesquisar_Colaborador = QPushButton(self.gb_Itens_Recarga)
        self.bt_Pesquisar_Colaborador.setObjectName(u"bt_Pesquisar_Colaborador")
        self.bt_Pesquisar_Colaborador.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Colaborador.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Pesquisar_Colaborador)

        self.txt_Nome = QLineEdit(self.gb_Itens_Recarga)
        self.txt_Nome.setObjectName(u"txt_Nome")
        self.txt_Nome.setMinimumSize(QSize(0, 30))
        self.txt_Nome.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.txt_Nome)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.lb_Carga = QLabel(self.gb_Itens_Recarga)
        self.lb_Carga.setObjectName(u"lb_Carga")
        self.lb_Carga.setMinimumSize(QSize(0, 30))
        self.lb_Carga.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.lb_Carga)

        self.txt_Carga = QLineEdit(self.gb_Itens_Recarga)
        self.txt_Carga.setObjectName(u"txt_Carga")
        self.txt_Carga.setMinimumSize(QSize(80, 30))
        self.txt_Carga.setMaximumSize(QSize(80, 30))

        self.horizontalLayout_7.addWidget(self.txt_Carga)

        self.lb_Sem_Carga = QLabel(self.gb_Itens_Recarga)
        self.lb_Sem_Carga.setObjectName(u"lb_Sem_Carga")
        self.lb_Sem_Carga.setMinimumSize(QSize(0, 30))
        self.lb_Sem_Carga.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.lb_Sem_Carga)

        self.txt_Sem_Carga = QLineEdit(self.gb_Itens_Recarga)
        self.txt_Sem_Carga.setObjectName(u"txt_Sem_Carga")
        self.txt_Sem_Carga.setMinimumSize(QSize(0, 30))
        self.txt_Sem_Carga.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.txt_Sem_Carga)

        self.lb_Valor = QLabel(self.gb_Itens_Recarga)
        self.lb_Valor.setObjectName(u"lb_Valor")
        self.lb_Valor.setMinimumSize(QSize(0, 30))
        self.lb_Valor.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.lb_Valor)

        self.dbs_Valor = QDoubleSpinBox(self.gb_Itens_Recarga)
        self.dbs_Valor.setObjectName(u"dbs_Valor")
        self.dbs_Valor.setMinimumSize(QSize(150, 30))
        self.dbs_Valor.setMaximumSize(QSize(150, 30))

        self.horizontalLayout_7.addWidget(self.dbs_Valor)

        self.bt_Confirmar_Item = QPushButton(self.gb_Itens_Recarga)
        self.bt_Confirmar_Item.setObjectName(u"bt_Confirmar_Item")
        self.bt_Confirmar_Item.setMinimumSize(QSize(0, 30))
        self.bt_Confirmar_Item.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.bt_Confirmar_Item)

        self.bt_Limpar_Item = QPushButton(self.gb_Itens_Recarga)
        self.bt_Limpar_Item.setObjectName(u"bt_Limpar_Item")
        self.bt_Limpar_Item.setMinimumSize(QSize(0, 30))
        self.bt_Limpar_Item.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.bt_Limpar_Item)

        self.bt_Excluir_Item = QPushButton(self.gb_Itens_Recarga)
        self.bt_Excluir_Item.setObjectName(u"bt_Excluir_Item")
        self.bt_Excluir_Item.setMinimumSize(QSize(0, 30))
        self.bt_Excluir_Item.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.bt_Excluir_Item)


        self.verticalLayout_4.addLayout(self.horizontalLayout_7)


        self.verticalLayout.addWidget(self.gb_Itens_Recarga)

        self.tb_Itens = QTableView(Lancamento_Recargas)
        self.tb_Itens.setObjectName(u"tb_Itens")

        self.verticalLayout.addWidget(self.tb_Itens)

        self.lb_Dica = QLabel(Lancamento_Recargas)
        self.lb_Dica.setObjectName(u"lb_Dica")

        self.verticalLayout.addWidget(self.lb_Dica)

        self.frm_Total = QFrame(Lancamento_Recargas)
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


        self.verticalLayout.addWidget(self.frm_Total)

        self.frm_Crud = QFrame(Lancamento_Recargas)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.bt_Sair_Recarga = QPushButton(self.frm_Crud)
        self.bt_Sair_Recarga.setObjectName(u"bt_Sair_Recarga")

        self.horizontalLayout_3.addWidget(self.bt_Sair_Recarga)

        self.horizontalSpacer_3 = QSpacerItem(448, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

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
        self.gb_Identificacao.setTitle(QCoreApplication.translate("Lancamento_Recargas", u"Identifica\u00e7\u00e3o", None))
        self.lb_Recargas.setText(QCoreApplication.translate("Lancamento_Recargas", u"Recargas:", None))
        self.bt_Pesquisar_Recargas.setText(QCoreApplication.translate("Lancamento_Recargas", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Lancamento_Recargas", u"+", None))
        self.lb_Data.setText(QCoreApplication.translate("Lancamento_Recargas", u"Data:", None))
        self.bt_Abrir_Recargas.setText(QCoreApplication.translate("Lancamento_Recargas", u"Abrir Recarga", None))
        self.gb_Itens_Recarga.setTitle(QCoreApplication.translate("Lancamento_Recargas", u"Itens da Recarga", None))
        self.lb_Colaboradores.setText(QCoreApplication.translate("Lancamento_Recargas", u"Colaboradores:", None))
        self.bt_Pesquisar_Colaborador.setText(QCoreApplication.translate("Lancamento_Recargas", u"...", None))
        self.lb_Carga.setText(QCoreApplication.translate("Lancamento_Recargas", u"Carga:", None))
        self.lb_Sem_Carga.setText(QCoreApplication.translate("Lancamento_Recargas", u"Sem Carga:", None))
        self.lb_Valor.setText(QCoreApplication.translate("Lancamento_Recargas", u"Valor:", None))
        self.dbs_Valor.setPrefix(QCoreApplication.translate("Lancamento_Recargas", u"R$ ", None))
        self.bt_Confirmar_Item.setText(QCoreApplication.translate("Lancamento_Recargas", u"Confirmar", None))
        self.bt_Limpar_Item.setText(QCoreApplication.translate("Lancamento_Recargas", u"Limpar Item", None))
        self.bt_Excluir_Item.setText(QCoreApplication.translate("Lancamento_Recargas", u"Excluir Item", None))
        self.lb_Dica.setText(QCoreApplication.translate("Lancamento_Recargas", u"Duplo clique no item para editar \u00b7 Selecione e Excluir Item para remover", None))
        self.lb_Total.setText(QCoreApplication.translate("Lancamento_Recargas", u"Total:", None))
        self.bt_Sair_Recarga.setText(QCoreApplication.translate("Lancamento_Recargas", u"Sair Recarga", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Lancamento_Recargas", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Lancamento_Recargas", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Lancamento_Recargas", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Lancamento_Recargas", u"Excluir", None))
    # retranslateUi

