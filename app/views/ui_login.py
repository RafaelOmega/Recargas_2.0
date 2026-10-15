# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loginuckZlJ.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTextBrowser, QVBoxLayout, QWidget)

class Ui_Login(object):
    def setupUi(self, Login):
        if not Login.objectName():
            Login.setObjectName(u"Login")
        Login.resize(400, 228)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        Login.setFont(font)
        self.verticalLayout = QVBoxLayout(Login)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.txt_Titulo = QTextBrowser(Login)
        self.txt_Titulo.setObjectName(u"txt_Titulo")

        self.verticalLayout.addWidget(self.txt_Titulo)

        self.frame = QFrame(Login)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.lb_Usuario = QLabel(self.frame)
        self.lb_Usuario.setObjectName(u"lb_Usuario")
        self.lb_Usuario.setMinimumSize(QSize(0, 30))
        self.lb_Usuario.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Usuario, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.txt_Usuario = QLineEdit(self.frame)
        self.txt_Usuario.setObjectName(u"txt_Usuario")
        self.txt_Usuario.setMinimumSize(QSize(0, 30))
        self.txt_Usuario.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.txt_Usuario, 0, 1, 1, 1)

        self.lb_Senha = QLabel(self.frame)
        self.lb_Senha.setObjectName(u"lb_Senha")
        self.lb_Senha.setMinimumSize(QSize(0, 30))
        self.lb_Senha.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Senha, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.txt_Senha = QLineEdit(self.frame)
        self.txt_Senha.setObjectName(u"txt_Senha")
        self.txt_Senha.setMinimumSize(QSize(0, 30))
        self.txt_Senha.setMaximumSize(QSize(16777215, 30))
        self.txt_Senha.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.txt_Senha, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.frame)

        self.bt_Entrar = QPushButton(Login)
        self.bt_Entrar.setObjectName(u"bt_Entrar")
        self.bt_Entrar.setMinimumSize(QSize(0, 30))
        self.bt_Entrar.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout.addWidget(self.bt_Entrar)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(Login)

        QMetaObject.connectSlotsByName(Login)
    # setupUi

    def retranslateUi(self, Login):
        Login.setWindowTitle(QCoreApplication.translate("Login", u"Login", None))
        self.txt_Titulo.setHtml(QCoreApplication.translate("Login", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI Semibold'; font-size:12pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Controle de Recargas de Cart\u00f5es Beneficio </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">e </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-righ"
                        "t:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Abastecimento</span></p></body></html>", None))
        self.lb_Usuario.setText(QCoreApplication.translate("Login", u"Usuario:", None))
        self.lb_Senha.setText(QCoreApplication.translate("Login", u"Senha:", None))
        self.bt_Entrar.setText(QCoreApplication.translate("Login", u"Entrar", None))
    # retranslateUi

