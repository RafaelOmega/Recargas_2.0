# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'cad_usuariosxEwVOJ.ui'
##
# Created by: Qt User Interface Compiler version 6.11.2
##
# WARNING! All changes made in this file will be lost when recompiling UI file!
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


class Ui_Cad_Usuarios(object):
    def setupUi(self, Cad_Usuarios):
        if not Cad_Usuarios.objectName():
            Cad_Usuarios.setObjectName(u"Cad_Usuarios")
        Cad_Usuarios.resize(538, 221)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Cad_Usuarios.setFont(font)
        self.verticalLayout = QVBoxLayout(Cad_Usuarios)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Codigo = QFrame(Cad_Usuarios)
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

        self.bt_Pesquisar_Usuario = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Usuario.setObjectName(u"bt_Pesquisar_Usuario")
        self.bt_Pesquisar_Usuario.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Usuario.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Pesquisar_Usuario)

        self.bt_Novo = QPushButton(self.frm_Codigo)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(
            253, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addWidget(self.frm_Codigo)

        self.frm_Corpo = QFrame(Cad_Usuarios)
        self.frm_Corpo.setObjectName(u"frm_Corpo")
        self.frm_Corpo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Corpo.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frm_Corpo)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.txt_Documento = QLineEdit(self.frm_Corpo)
        self.txt_Documento.setObjectName(u"txt_Documento")
        self.txt_Documento.setMinimumSize(QSize(180, 30))
        self.txt_Documento.setMaximumSize(QSize(180, 30))

        self.gridLayout.addWidget(self.txt_Documento, 3, 1, 1, 1)

        self.lb_Documento = QLabel(self.frm_Corpo)
        self.lb_Documento.setObjectName(u"lb_Documento")
        self.lb_Documento.setMinimumSize(QSize(0, 30))
        self.lb_Documento.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(
            self.lb_Documento, 3, 0, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.lb_Nome = QLabel(self.frm_Corpo)
        self.lb_Nome.setObjectName(u"lb_Nome")
        self.lb_Nome.setMinimumSize(QSize(0, 30))
        self.lb_Nome.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Nome, 2, 0, 1, 1)

        self.chk_Ativo = QCheckBox(self.frm_Corpo)
        self.chk_Ativo.setObjectName(u"chk_Ativo")
        self.chk_Ativo.setChecked(True)

        self.gridLayout.addWidget(self.chk_Ativo, 3, 3, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 3, 4, 1, 1)

        self.txt_Nome = QLineEdit(self.frm_Corpo)
        self.txt_Nome.setObjectName(u"txt_Nome")
        self.txt_Nome.setMinimumSize(QSize(0, 30))
        self.txt_Nome.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.txt_Nome, 2, 1, 1, 4)

        self.verticalLayout.addWidget(self.frm_Corpo)

        self.frm_Usuario = QFrame(Cad_Usuarios)
        self.frm_Usuario.setObjectName(u"frm_Usuario")
        self.frm_Usuario.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Usuario.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Usuario)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Usuario = QLabel(self.frm_Usuario)
        self.lb_Usuario.setObjectName(u"lb_Usuario")
        self.lb_Usuario.setMinimumSize(QSize(0, 30))
        self.lb_Usuario.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Usuario)

        self.txt_Usuario = QLineEdit(self.frm_Usuario)
        self.txt_Usuario.setObjectName(u"txt_Usuario")
        self.txt_Usuario.setMinimumSize(QSize(0, 30))
        self.txt_Usuario.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.txt_Usuario)

        self.lb_Senha = QLabel(self.frm_Usuario)
        self.lb_Senha.setObjectName(u"lb_Senha")
        self.lb_Senha.setMinimumSize(QSize(0, 30))
        self.lb_Senha.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Senha)

        self.txt_Senha = QLineEdit(self.frm_Usuario)
        self.txt_Senha.setObjectName(u"txt_Senha")
        self.txt_Senha.setMinimumSize(QSize(0, 30))
        self.txt_Senha.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.txt_Senha)

        self.verticalLayout.addWidget(self.frm_Usuario)

        self.frm_Crud = QFrame(Cad_Usuarios)
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

        self.horizontalSpacer_3 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        self.retranslateUi(Cad_Usuarios)

        QMetaObject.connectSlotsByName(Cad_Usuarios)
    # setupUi

    def retranslateUi(self, Cad_Usuarios):
        Cad_Usuarios.setWindowTitle(QCoreApplication.translate(
            "Cad_Usuarios", u"Cadastro de Usuarios", None))
        self.lb_Codigo.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"C\u00f3digo:", None))
        self.txt_Codigo.setText("")
        self.bt_Pesquisar_Usuario.setText(
            QCoreApplication.translate("Cad_Usuarios", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"+", None))
        self.lb_Documento.setText(
            QCoreApplication.translate("Cad_Usuarios", u"CPF:", None))
        self.lb_Nome.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Nome:", None))
        self.chk_Ativo.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Ativo", None))
        self.lb_Usuario.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Usuario:", None))
        self.lb_Senha.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Senha:", None))
        self.bt_Salvar.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate(
            "Cad_Usuarios", u"Excluir", None))
    # retranslateUi
