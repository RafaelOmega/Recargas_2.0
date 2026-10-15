# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pesquisa_colaboradorhFjNPv.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QTableView, QVBoxLayout,
    QWidget)

class Ui_Pesquisa_Colaborador(object):
    def setupUi(self, Pesquisa_Colaborador):
        if not Pesquisa_Colaborador.objectName():
            Pesquisa_Colaborador.setObjectName(u"Pesquisa_Colaborador")
        Pesquisa_Colaborador.resize(657, 450)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Pesquisa_Colaborador.setFont(font)
        self.verticalLayout = QVBoxLayout(Pesquisa_Colaborador)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Filtro = QFrame(Pesquisa_Colaborador)
        self.frm_Filtro.setObjectName(u"frm_Filtro")
        self.frm_Filtro.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Filtro.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_Filtro)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.lb_Pesquisa = QLabel(self.frm_Filtro)
        self.lb_Pesquisa.setObjectName(u"lb_Pesquisa")
        self.lb_Pesquisa.setMinimumSize(QSize(0, 30))
        self.lb_Pesquisa.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Pesquisa)

        self.txt_Pesquisa = QLineEdit(self.frm_Filtro)
        self.txt_Pesquisa.setObjectName(u"txt_Pesquisa")
        self.txt_Pesquisa.setMinimumSize(QSize(0, 30))
        self.txt_Pesquisa.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.txt_Pesquisa)

        self.rb_Ativo = QRadioButton(self.frm_Filtro)
        self.rb_Ativo.setObjectName(u"rb_Ativo")
        self.rb_Ativo.setMinimumSize(QSize(0, 30))
        self.rb_Ativo.setMaximumSize(QSize(16777215, 30))
        self.rb_Ativo.setChecked(True)

        self.horizontalLayout.addWidget(self.rb_Ativo)

        self.rb_Inativo = QRadioButton(self.frm_Filtro)
        self.rb_Inativo.setObjectName(u"rb_Inativo")
        self.rb_Inativo.setMinimumSize(QSize(0, 30))
        self.rb_Inativo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.rb_Inativo)

        self.bt_Pesquisa = QPushButton(self.frm_Filtro)
        self.bt_Pesquisa.setObjectName(u"bt_Pesquisa")
        self.bt_Pesquisa.setMinimumSize(QSize(0, 30))
        self.bt_Pesquisa.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.bt_Pesquisa)


        self.verticalLayout.addWidget(self.frm_Filtro)

        self.frm_Lista = QFrame(Pesquisa_Colaborador)
        self.frm_Lista.setObjectName(u"frm_Lista")
        self.frm_Lista.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Lista.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Lista)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.tb_Colaborador = QTableView(self.frm_Lista)
        self.tb_Colaborador.setObjectName(u"tb_Colaborador")

        self.verticalLayout_2.addWidget(self.tb_Colaborador)


        self.verticalLayout.addWidget(self.frm_Lista)


        self.retranslateUi(Pesquisa_Colaborador)

        QMetaObject.connectSlotsByName(Pesquisa_Colaborador)
    # setupUi

    def retranslateUi(self, Pesquisa_Colaborador):
        Pesquisa_Colaborador.setWindowTitle(QCoreApplication.translate("Pesquisa_Colaborador", u"Pesquisa Colaborador", None))
        self.lb_Pesquisa.setText(QCoreApplication.translate("Pesquisa_Colaborador", u"Pesquisar:", None))
        self.rb_Ativo.setText(QCoreApplication.translate("Pesquisa_Colaborador", u"Ativos", None))
        self.rb_Inativo.setText(QCoreApplication.translate("Pesquisa_Colaborador", u"Inativos", None))
        self.bt_Pesquisa.setText(QCoreApplication.translate("Pesquisa_Colaborador", u"Confirmar", None))
    # retranslateUi

