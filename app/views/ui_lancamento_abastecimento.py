# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'lancamento_abastecimentoAJTFib.ui'
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
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTableView, QVBoxLayout,
    QWidget)

class Ui_Lancamento_Abastecimento(object):
    def setupUi(self, Lancamento_Abastecimento):
        if not Lancamento_Abastecimento.objectName():
            Lancamento_Abastecimento.setObjectName(u"Lancamento_Abastecimento")
        Lancamento_Abastecimento.resize(1182, 680)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Lancamento_Abastecimento.setFont(font)
        self.verticalLayout = QVBoxLayout(Lancamento_Abastecimento)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, 10, 12, 10)
        self.grp_Identificacao = QGroupBox(Lancamento_Abastecimento)
        self.grp_Identificacao.setObjectName(u"grp_Identificacao")
        self.hl_Identificacao = QHBoxLayout(self.grp_Identificacao)
        self.hl_Identificacao.setSpacing(8)
        self.hl_Identificacao.setObjectName(u"hl_Identificacao")
        self.hl_Identificacao.setContentsMargins(10, 4, 10, 8)
        self.lb_Abastecimento = QLabel(self.grp_Identificacao)
        self.lb_Abastecimento.setObjectName(u"lb_Abastecimento")
        self.lb_Abastecimento.setMinimumSize(QSize(0, 30))
        self.lb_Abastecimento.setMaximumSize(QSize(16777215, 30))

        self.hl_Identificacao.addWidget(self.lb_Abastecimento)

        self.txt_Abastecimento = QLineEdit(self.grp_Identificacao)
        self.txt_Abastecimento.setObjectName(u"txt_Abastecimento")
        self.txt_Abastecimento.setMinimumSize(QSize(110, 30))
        self.txt_Abastecimento.setMaximumSize(QSize(110, 30))

        self.hl_Identificacao.addWidget(self.txt_Abastecimento)

        self.bt_Pesquisar_Abastecimentos = QPushButton(self.grp_Identificacao)
        self.bt_Pesquisar_Abastecimentos.setObjectName(u"bt_Pesquisar_Abastecimentos")
        self.bt_Pesquisar_Abastecimentos.setMinimumSize(QSize(0, 30))
        self.bt_Pesquisar_Abastecimentos.setMaximumSize(QSize(44, 30))

        self.hl_Identificacao.addWidget(self.bt_Pesquisar_Abastecimentos)

        self.bt_Novo = QPushButton(self.grp_Identificacao)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(0, 30))
        self.bt_Novo.setMaximumSize(QSize(44, 30))

        self.hl_Identificacao.addWidget(self.bt_Novo)

        self.sp_Identificacao = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_Identificacao.addItem(self.sp_Identificacao)

        self.lb_Data = QLabel(self.grp_Identificacao)
        self.lb_Data.setObjectName(u"lb_Data")
        self.lb_Data.setMinimumSize(QSize(0, 30))
        self.lb_Data.setMaximumSize(QSize(16777215, 30))

        self.hl_Identificacao.addWidget(self.lb_Data)

        self.dt_Data = QDateEdit(self.grp_Identificacao)
        self.dt_Data.setObjectName(u"dt_Data")
        self.dt_Data.setMinimumSize(QSize(130, 30))
        self.dt_Data.setMaximumSize(QSize(16777215, 30))
        self.dt_Data.setCalendarPopup(True)

        self.hl_Identificacao.addWidget(self.dt_Data)

        self.bt_Abrir_Abastecimento = QPushButton(self.grp_Identificacao)
        self.bt_Abrir_Abastecimento.setObjectName(u"bt_Abrir_Abastecimento")
        self.bt_Abrir_Abastecimento.setMinimumSize(QSize(0, 30))
        self.bt_Abrir_Abastecimento.setMaximumSize(QSize(16777215, 30))

        self.hl_Identificacao.addWidget(self.bt_Abrir_Abastecimento)


        self.verticalLayout.addWidget(self.grp_Identificacao)

        self.grp_Vinculos = QGroupBox(Lancamento_Abastecimento)
        self.grp_Vinculos.setObjectName(u"grp_Vinculos")
        self.gl_Vinculos = QGridLayout(self.grp_Vinculos)
        self.gl_Vinculos.setObjectName(u"gl_Vinculos")
        self.gl_Vinculos.setHorizontalSpacing(8)
        self.gl_Vinculos.setVerticalSpacing(6)
        self.gl_Vinculos.setContentsMargins(10, 4, 10, 8)
        self.lb_Caminhao = QLabel(self.grp_Vinculos)
        self.lb_Caminhao.setObjectName(u"lb_Caminhao")
        self.lb_Caminhao.setMinimumSize(QSize(0, 30))
        self.lb_Caminhao.setMaximumSize(QSize(16777215, 30))

        self.gl_Vinculos.addWidget(self.lb_Caminhao, 0, 0, 1, 1)

        self.txt_Cod_Caminhao = QLineEdit(self.grp_Vinculos)
        self.txt_Cod_Caminhao.setObjectName(u"txt_Cod_Caminhao")
        self.txt_Cod_Caminhao.setMinimumSize(QSize(110, 30))
        self.txt_Cod_Caminhao.setMaximumSize(QSize(110, 30))

        self.gl_Vinculos.addWidget(self.txt_Cod_Caminhao, 0, 1, 1, 1)

        self.bt_Pesquisar_Caminhao = QPushButton(self.grp_Vinculos)
        self.bt_Pesquisar_Caminhao.setObjectName(u"bt_Pesquisar_Caminhao")
        self.bt_Pesquisar_Caminhao.setMinimumSize(QSize(0, 30))
        self.bt_Pesquisar_Caminhao.setMaximumSize(QSize(44, 30))

        self.gl_Vinculos.addWidget(self.bt_Pesquisar_Caminhao, 0, 2, 1, 1)

        self.txt_Modelo = QLineEdit(self.grp_Vinculos)
        self.txt_Modelo.setObjectName(u"txt_Modelo")
        self.txt_Modelo.setMinimumSize(QSize(0, 30))
        self.txt_Modelo.setMaximumSize(QSize(16777215, 30))
        self.txt_Modelo.setReadOnly(True)

        self.gl_Vinculos.addWidget(self.txt_Modelo, 0, 3, 1, 1)

        self.lb_Colaborador = QLabel(self.grp_Vinculos)
        self.lb_Colaborador.setObjectName(u"lb_Colaborador")
        self.lb_Colaborador.setMinimumSize(QSize(0, 30))
        self.lb_Colaborador.setMaximumSize(QSize(16777215, 30))

        self.gl_Vinculos.addWidget(self.lb_Colaborador, 1, 0, 1, 1)

        self.txt_Cod_Colaborador = QLineEdit(self.grp_Vinculos)
        self.txt_Cod_Colaborador.setObjectName(u"txt_Cod_Colaborador")
        self.txt_Cod_Colaborador.setMinimumSize(QSize(110, 30))
        self.txt_Cod_Colaborador.setMaximumSize(QSize(110, 30))

        self.gl_Vinculos.addWidget(self.txt_Cod_Colaborador, 1, 1, 1, 1)

        self.bt_Pesquisar_Colaborador = QPushButton(self.grp_Vinculos)
        self.bt_Pesquisar_Colaborador.setObjectName(u"bt_Pesquisar_Colaborador")
        self.bt_Pesquisar_Colaborador.setMinimumSize(QSize(0, 30))
        self.bt_Pesquisar_Colaborador.setMaximumSize(QSize(44, 30))

        self.gl_Vinculos.addWidget(self.bt_Pesquisar_Colaborador, 1, 2, 1, 1)

        self.txt_Nome = QLineEdit(self.grp_Vinculos)
        self.txt_Nome.setObjectName(u"txt_Nome")
        self.txt_Nome.setMinimumSize(QSize(0, 30))
        self.txt_Nome.setMaximumSize(QSize(16777215, 30))
        self.txt_Nome.setReadOnly(True)

        self.gl_Vinculos.addWidget(self.txt_Nome, 1, 3, 1, 1)

        self.gl_Vinculos.setColumnStretch(3, 1)

        self.verticalLayout.addWidget(self.grp_Vinculos)

        self.grp_Item = QGroupBox(Lancamento_Abastecimento)
        self.grp_Item.setObjectName(u"grp_Item")
        self.hl_Item = QHBoxLayout(self.grp_Item)
        self.hl_Item.setSpacing(8)
        self.hl_Item.setObjectName(u"hl_Item")
        self.hl_Item.setContentsMargins(10, 4, 10, 8)
        self.lb_Destino = QLabel(self.grp_Item)
        self.lb_Destino.setObjectName(u"lb_Destino")
        self.lb_Destino.setMinimumSize(QSize(0, 30))
        self.lb_Destino.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.lb_Destino)

        self.txt_Destino = QLineEdit(self.grp_Item)
        self.txt_Destino.setObjectName(u"txt_Destino")
        self.txt_Destino.setMinimumSize(QSize(160, 30))
        self.txt_Destino.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.txt_Destino)

        self.lb_KM_Inicio = QLabel(self.grp_Item)
        self.lb_KM_Inicio.setObjectName(u"lb_KM_Inicio")
        self.lb_KM_Inicio.setMinimumSize(QSize(0, 30))
        self.lb_KM_Inicio.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.lb_KM_Inicio)

        self.spn_KM_Inicio = QSpinBox(self.grp_Item)
        self.spn_KM_Inicio.setObjectName(u"spn_KM_Inicio")
        self.spn_KM_Inicio.setMinimumSize(QSize(110, 30))
        self.spn_KM_Inicio.setMaximumSize(QSize(110, 30))
        self.spn_KM_Inicio.setMaximum(9999999)

        self.hl_Item.addWidget(self.spn_KM_Inicio)

        self.lb_KM_Final = QLabel(self.grp_Item)
        self.lb_KM_Final.setObjectName(u"lb_KM_Final")
        self.lb_KM_Final.setMinimumSize(QSize(0, 30))
        self.lb_KM_Final.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.lb_KM_Final)

        self.spn_KM_Final = QSpinBox(self.grp_Item)
        self.spn_KM_Final.setObjectName(u"spn_KM_Final")
        self.spn_KM_Final.setMinimumSize(QSize(110, 30))
        self.spn_KM_Final.setMaximumSize(QSize(110, 30))
        self.spn_KM_Final.setMaximum(9999999)

        self.hl_Item.addWidget(self.spn_KM_Final)

        self.lb_Litros = QLabel(self.grp_Item)
        self.lb_Litros.setObjectName(u"lb_Litros")
        self.lb_Litros.setMinimumSize(QSize(0, 30))
        self.lb_Litros.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.lb_Litros)

        self.dbs_Litros = QDoubleSpinBox(self.grp_Item)
        self.dbs_Litros.setObjectName(u"dbs_Litros")
        self.dbs_Litros.setMinimumSize(QSize(110, 30))
        self.dbs_Litros.setMaximumSize(QSize(110, 30))
        self.dbs_Litros.setDecimals(2)
        self.dbs_Litros.setMaximum(9999999.000000000000000)

        self.hl_Item.addWidget(self.dbs_Litros)

        self.bt_Confirmar_Item = QPushButton(self.grp_Item)
        self.bt_Confirmar_Item.setObjectName(u"bt_Confirmar_Item")
        self.bt_Confirmar_Item.setMinimumSize(QSize(0, 30))
        self.bt_Confirmar_Item.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.bt_Confirmar_Item)

        self.bt_Limpar_Item = QPushButton(self.grp_Item)
        self.bt_Limpar_Item.setObjectName(u"bt_Limpar_Item")
        self.bt_Limpar_Item.setMinimumSize(QSize(0, 30))
        self.bt_Limpar_Item.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.bt_Limpar_Item)

        self.bt_Excluir_Item = QPushButton(self.grp_Item)
        self.bt_Excluir_Item.setObjectName(u"bt_Excluir_Item")
        self.bt_Excluir_Item.setMinimumSize(QSize(0, 30))
        self.bt_Excluir_Item.setMaximumSize(QSize(16777215, 30))

        self.hl_Item.addWidget(self.bt_Excluir_Item)


        self.verticalLayout.addWidget(self.grp_Item)

        self.tb_Itens = QTableView(Lancamento_Abastecimento)
        self.tb_Itens.setObjectName(u"tb_Itens")
        self.tb_Itens.setAlternatingRowColors(True)

        self.verticalLayout.addWidget(self.tb_Itens)

        self.lb_Dica = QLabel(Lancamento_Abastecimento)
        self.lb_Dica.setObjectName(u"lb_Dica")
        self.lb_Dica.setMinimumSize(QSize(0, 30))
        self.lb_Dica.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout.addWidget(self.lb_Dica)

        self.hl_Total = QHBoxLayout()
        self.hl_Total.setSpacing(8)
        self.hl_Total.setObjectName(u"hl_Total")
        self.sp_Total = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_Total.addItem(self.sp_Total)

        self.lb_Total = QLabel(Lancamento_Abastecimento)
        self.lb_Total.setObjectName(u"lb_Total")
        self.lb_Total.setMinimumSize(QSize(0, 30))
        self.lb_Total.setMaximumSize(QSize(16777215, 30))

        self.hl_Total.addWidget(self.lb_Total)

        self.txt_Total = QLineEdit(Lancamento_Abastecimento)
        self.txt_Total.setObjectName(u"txt_Total")
        self.txt_Total.setMinimumSize(QSize(150, 30))
        self.txt_Total.setMaximumSize(QSize(150, 30))
        self.txt_Total.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.txt_Total.setReadOnly(True)

        self.hl_Total.addWidget(self.txt_Total)


        self.verticalLayout.addLayout(self.hl_Total)

        self.frm_Crud = QFrame(Lancamento_Abastecimento)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.hl_Crud = QHBoxLayout(self.frm_Crud)
        self.hl_Crud.setSpacing(8)
        self.hl_Crud.setObjectName(u"hl_Crud")
        self.hl_Crud.setContentsMargins(10, 6, 10, 6)
        self.bt_Sair_Abastecimento = QPushButton(self.frm_Crud)
        self.bt_Sair_Abastecimento.setObjectName(u"bt_Sair_Abastecimento")
        self.bt_Sair_Abastecimento.setMinimumSize(QSize(0, 30))
        self.bt_Sair_Abastecimento.setMaximumSize(QSize(16777215, 30))

        self.hl_Crud.addWidget(self.bt_Sair_Abastecimento)

        self.sp_Crud = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_Crud.addItem(self.sp_Crud)

        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.hl_Crud.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.hl_Crud.addWidget(self.bt_Editar)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.hl_Crud.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.hl_Crud.addWidget(self.bt_Excluir)


        self.verticalLayout.addWidget(self.frm_Crud)

        self.verticalLayout.setStretch(3, 1)

        self.retranslateUi(Lancamento_Abastecimento)

        QMetaObject.connectSlotsByName(Lancamento_Abastecimento)
    # setupUi

    def retranslateUi(self, Lancamento_Abastecimento):
        Lancamento_Abastecimento.setWindowTitle(QCoreApplication.translate("Lancamento_Abastecimento", u"Lan\u00e7amento de Abastecimento", None))
        self.grp_Identificacao.setTitle(QCoreApplication.translate("Lancamento_Abastecimento", u"Identifica\u00e7\u00e3o", None))
        self.lb_Abastecimento.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Abastecimento:", None))
#if QT_CONFIG(tooltip)
        self.txt_Abastecimento.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"C\u00f3digo do abastecimento (Enter busca; vazio abre a pesquisa)", None))
#endif // QT_CONFIG(tooltip)
        self.txt_Abastecimento.setPlaceholderText(QCoreApplication.translate("Lancamento_Abastecimento", u"C\u00f3digo", None))
#if QT_CONFIG(tooltip)
        self.bt_Pesquisar_Abastecimentos.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Pesquisar abastecimentos", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Pesquisar_Abastecimentos.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"...", None))
#if QT_CONFIG(tooltip)
        self.bt_Novo.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Novo abastecimento (F2)", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Novo.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"+", None))
        self.lb_Data.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Data:", None))
#if QT_CONFIG(tooltip)
        self.dt_Data.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Data do abastecimento", None))
#endif // QT_CONFIG(tooltip)
        self.dt_Data.setDisplayFormat(QCoreApplication.translate("Lancamento_Abastecimento", u"dd/MM/yyyy", None))
#if QT_CONFIG(tooltip)
        self.bt_Abrir_Abastecimento.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Abre o abastecimento para lan\u00e7amento dos itens", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Abrir_Abastecimento.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Abrir Abastecimento", None))
        self.grp_Vinculos.setTitle(QCoreApplication.translate("Lancamento_Abastecimento", u"V\u00ednculos", None))
        self.lb_Caminhao.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Caminh\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.txt_Cod_Caminhao.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"C\u00f3digo do caminh\u00e3o (Enter busca; vazio abre a pesquisa)", None))
#endif // QT_CONFIG(tooltip)
        self.txt_Cod_Caminhao.setPlaceholderText(QCoreApplication.translate("Lancamento_Abastecimento", u"C\u00f3digo", None))
#if QT_CONFIG(tooltip)
        self.bt_Pesquisar_Caminhao.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Pesquisar caminh\u00f5es", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Pesquisar_Caminhao.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"...", None))
#if QT_CONFIG(tooltip)
        self.txt_Modelo.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Modelo do caminh\u00e3o selecionado", None))
#endif // QT_CONFIG(tooltip)
        self.lb_Colaborador.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Colaborador:", None))
#if QT_CONFIG(tooltip)
        self.txt_Cod_Colaborador.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"C\u00f3digo do colaborador (Enter busca; vazio abre a pesquisa)", None))
#endif // QT_CONFIG(tooltip)
        self.txt_Cod_Colaborador.setPlaceholderText(QCoreApplication.translate("Lancamento_Abastecimento", u"C\u00f3digo", None))
#if QT_CONFIG(tooltip)
        self.bt_Pesquisar_Colaborador.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Pesquisar colaboradores", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Pesquisar_Colaborador.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"...", None))
#if QT_CONFIG(tooltip)
        self.txt_Nome.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Nome do colaborador selecionado", None))
#endif // QT_CONFIG(tooltip)
        self.grp_Item.setTitle(QCoreApplication.translate("Lancamento_Abastecimento", u"Item do abastecimento", None))
        self.lb_Destino.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Destino:", None))
        self.txt_Destino.setPlaceholderText(QCoreApplication.translate("Lancamento_Abastecimento", u"Ex.: Centro \u2014 Dep\u00f3sito", None))
        self.lb_KM_Inicio.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"KM In\u00edcio:", None))
        self.lb_KM_Final.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"KM Final:", None))
        self.lb_Litros.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Qtde LTs.:", None))
#if QT_CONFIG(tooltip)
        self.bt_Confirmar_Item.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Confirma o item na grade (Enter no campo tamb\u00e9m confirma)", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Confirmar_Item.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Confirmar", None))
#if QT_CONFIG(tooltip)
        self.bt_Limpar_Item.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Limpa os campos do item", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Limpar_Item.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Limpar Item", None))
#if QT_CONFIG(tooltip)
        self.bt_Excluir_Item.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Exclui o item selecionado na grade", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Excluir_Item.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Excluir Item", None))
        self.lb_Dica.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Duplo clique no item para editar \u00b7 Selecione e Excluir Item para remover", None))
        self.lb_Total.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Total:", None))
#if QT_CONFIG(tooltip)
        self.txt_Total.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Total de litros do abastecimento", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.bt_Sair_Abastecimento.setToolTip(QCoreApplication.translate("Lancamento_Abastecimento", u"Finaliza o lan\u00e7amento dos itens e libera o Salvar", None))
#endif // QT_CONFIG(tooltip)
        self.bt_Sair_Abastecimento.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Sair Abastecimento", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Lancamento_Abastecimento", u"Excluir", None))
    # retranslateUi

