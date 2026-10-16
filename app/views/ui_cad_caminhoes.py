# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cad_caminhoesRyOSan.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Cad_Caminhoes(object):
    def setupUi(self, Cad_Caminhoes):
        if not Cad_Caminhoes.objectName():
            Cad_Caminhoes.setObjectName(u"Cad_Caminhoes")
        Cad_Caminhoes.resize(479, 177)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Cad_Caminhoes.setFont(font)
        self.verticalLayout = QVBoxLayout(Cad_Caminhoes)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Codigo = QFrame(Cad_Caminhoes)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.lb_Codigo = QLabel(self.frm_Codigo)
        self.lb_Codigo.setObjectName(u"lb_Codigo")
        self.lb_Codigo.setMinimumSize(QSize(0, 30))
        self.lb_Codigo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Codigo)

        self.txt_Codigo = QLineEdit(self.frm_Codigo)
        self.txt_Codigo.setObjectName(u"txt_Codigo")
        self.txt_Codigo.setMinimumSize(QSize(100, 30))
        self.txt_Codigo.setMaximumSize(QSize(100, 30))

        self.horizontalLayout.addWidget(self.txt_Codigo)

        self.bt_Pesquisar_Caminhoes = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Caminhoes.setObjectName(u"bt_Pesquisar_Caminhoes")
        self.bt_Pesquisar_Caminhoes.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Caminhoes.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Pesquisar_Caminhoes)

        self.bt_Novo = QPushButton(self.frm_Codigo)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(253, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frm_Codigo)

        self.frm_Corpo = QFrame(Cad_Caminhoes)
        self.frm_Corpo.setObjectName(u"frm_Corpo")
        self.frm_Corpo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Corpo.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frm_Corpo)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 4, 1, 1)

        self.chk_Ativo = QCheckBox(self.frm_Corpo)
        self.chk_Ativo.setObjectName(u"chk_Ativo")
        self.chk_Ativo.setChecked(True)

        self.gridLayout.addWidget(self.chk_Ativo, 1, 3, 1, 1)

        self.lb_Modelo = QLabel(self.frm_Corpo)
        self.lb_Modelo.setObjectName(u"lb_Modelo")
        self.lb_Modelo.setMinimumSize(QSize(0, 30))
        self.lb_Modelo.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Modelo, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.txt_Placa = QLineEdit(self.frm_Corpo)
        self.txt_Placa.setObjectName(u"txt_Placa")
        self.txt_Placa.setMinimumSize(QSize(180, 30))
        self.txt_Placa.setMaximumSize(QSize(180, 30))

        self.gridLayout.addWidget(self.txt_Placa, 1, 1, 1, 1)

        self.txt_Modelo = QLineEdit(self.frm_Corpo)
        self.txt_Modelo.setObjectName(u"txt_Modelo")
        self.txt_Modelo.setMinimumSize(QSize(0, 30))
        self.txt_Modelo.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.txt_Modelo, 0, 1, 1, 4)

        self.lb_Placa = QLabel(self.frm_Corpo)
        self.lb_Placa.setObjectName(u"lb_Placa")
        self.lb_Placa.setMinimumSize(QSize(0, 30))
        self.lb_Placa.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Placa, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout.addWidget(self.frm_Corpo)

        self.frm_Crud = QFrame(Cad_Caminhoes)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Editar)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Excluir)


        self.verticalLayout.addWidget(self.frm_Crud)


        self.retranslateUi(Cad_Caminhoes)

        QMetaObject.connectSlotsByName(Cad_Caminhoes)
    # setupUi

    def retranslateUi(self, Cad_Caminhoes):
        Cad_Caminhoes.setWindowTitle(QCoreApplication.translate("Cad_Caminhoes", u"Cadastro de Caminh\u00f5es", None))
        self.lb_Codigo.setText(QCoreApplication.translate("Cad_Caminhoes", u"C\u00f3digo:", None))
        self.txt_Codigo.setText("")
        self.bt_Pesquisar_Caminhoes.setText(QCoreApplication.translate("Cad_Caminhoes", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Cad_Caminhoes", u"+", None))
        self.chk_Ativo.setText(QCoreApplication.translate("Cad_Caminhoes", u"Ativo", None))
        self.lb_Modelo.setText(QCoreApplication.translate("Cad_Caminhoes", u"Modelo:", None))
        self.lb_Placa.setText(QCoreApplication.translate("Cad_Caminhoes", u"Placa:", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Cad_Caminhoes", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Cad_Caminhoes", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Cad_Caminhoes", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Cad_Caminhoes", u"Excluir", None))
    # retranslateUi

