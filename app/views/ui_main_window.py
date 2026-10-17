# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowQXPZbq.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QDateEdit, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMdiArea, QMenu, QMenuBar, QSizePolicy,
    QSpacerItem, QTimeEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 600)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(12)
        font.setBold(True)
        MainWindow.setFont(font)
        self.actionCad_Colaboradores = QAction(MainWindow)
        self.actionCad_Colaboradores.setObjectName(u"actionCad_Colaboradores")
        self.actionRecargas = QAction(MainWindow)
        self.actionRecargas.setObjectName(u"actionRecargas")
        self.actionSaldo_BIZ = QAction(MainWindow)
        self.actionSaldo_BIZ.setObjectName(u"actionSaldo_BIZ")
        self.actionRecarga_Colaborador = QAction(MainWindow)
        self.actionRecarga_Colaborador.setObjectName(u"actionRecarga_Colaborador")
        self.actionUsuarios = QAction(MainWindow)
        self.actionUsuarios.setObjectName(u"actionUsuarios")
        self.actionDash_Refeicao = QAction(MainWindow)
        self.actionDash_Refeicao.setObjectName(u"actionDash_Refeicao")
        self.actionCaminhoes = QAction(MainWindow)
        self.actionCaminhoes.setObjectName(u"actionCaminhoes")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mdiArea = QMdiArea(self.centralwidget)
        self.mdiArea.setObjectName(u"mdiArea")
        self.mdiArea.setStyleSheet(u"QMdiArea#mdiArea {\n"
"	background-color: #16222F;\n"
"}")

        self.verticalLayout.addWidget(self.mdiArea)

        self.frm_StatusBar = QFrame(self.centralwidget)
        self.frm_StatusBar.setObjectName(u"frm_StatusBar")
        self.frm_StatusBar.setStyleSheet(u"QFrame#frm_StatusBar {\n"
"	background-color: #1F3B5B;\n"
"	border: none;\n"
"	border-top: 2px solid #2E5A8F;\n"
"}\n"
"QFrame#frm_StatusBar QLabel {\n"
"	color: #D7E3F4;\n"
"	background: transparent;\n"
"}\n"
"QFrame#frm_StatusBar QLabel#lb_Comandos {\n"
"	color: #9FB8D8;\n"
"}\n"
"QFrame#frm_StatusBar QLabel#lb_Versao {\n"
"	color: #8FA8C6;\n"
"}\n"
"QFrame#frm_StatusBar QDateEdit,\n"
"QFrame#frm_StatusBar QTimeEdit {\n"
"	background: transparent;\n"
"	color: #B9CCE4;\n"
"	border: none;\n"
"}")
        self.frm_StatusBar.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_StatusBar.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_StatusBar)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(12, 4, 12, 4)
        self.lb_Comandos = QLabel(self.frm_StatusBar)
        self.lb_Comandos.setObjectName(u"lb_Comandos")
        self.lb_Comandos.setMinimumSize(QSize(0, 30))
        self.lb_Comandos.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Comandos)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lb_Saldo_Conta = QLabel(self.frm_StatusBar)
        self.lb_Saldo_Conta.setObjectName(u"lb_Saldo_Conta")
        self.lb_Saldo_Conta.setMinimumSize(QSize(0, 30))
        self.lb_Saldo_Conta.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Saldo_Conta)

        self.txt_Saldo_Conta = QLineEdit(self.frm_StatusBar)
        self.txt_Saldo_Conta.setObjectName(u"txt_Saldo_Conta")
        self.txt_Saldo_Conta.setMinimumSize(QSize(150, 30))
        self.txt_Saldo_Conta.setMaximumSize(QSize(150, 30))
        self.txt_Saldo_Conta.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.txt_Saldo_Conta.setReadOnly(True)

        self.horizontalLayout.addWidget(self.txt_Saldo_Conta)

        self.dt_Data_Atual = QDateEdit(self.frm_StatusBar)
        self.dt_Data_Atual.setObjectName(u"dt_Data_Atual")
        self.dt_Data_Atual.setEnabled(False)
        self.dt_Data_Atual.setMinimumSize(QSize(0, 30))
        self.dt_Data_Atual.setMaximumSize(QSize(16777215, 30))
        self.dt_Data_Atual.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dt_Data_Atual.setReadOnly(True)
        self.dt_Data_Atual.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.horizontalLayout.addWidget(self.dt_Data_Atual, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.dt_Hora_Atual = QTimeEdit(self.frm_StatusBar)
        self.dt_Hora_Atual.setObjectName(u"dt_Hora_Atual")
        self.dt_Hora_Atual.setEnabled(False)
        self.dt_Hora_Atual.setMinimumSize(QSize(0, 30))
        self.dt_Hora_Atual.setMaximumSize(QSize(16777215, 30))
        self.dt_Hora_Atual.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dt_Hora_Atual.setReadOnly(True)
        self.dt_Hora_Atual.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.horizontalLayout.addWidget(self.dt_Hora_Atual, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.lb_Versao = QLabel(self.frm_StatusBar)
        self.lb_Versao.setObjectName(u"lb_Versao")
        self.lb_Versao.setMinimumSize(QSize(0, 30))
        self.lb_Versao.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Versao)

        self.horizontalSpacer_2 = QSpacerItem(5, 30, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addWidget(self.frm_StatusBar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 33))
        self.menuCadastros = QMenu(self.menubar)
        self.menuCadastros.setObjectName(u"menuCadastros")
        self.menuLancamentos = QMenu(self.menubar)
        self.menuLancamentos.setObjectName(u"menuLancamentos")
        self.menuRelatorios = QMenu(self.menubar)
        self.menuRelatorios.setObjectName(u"menuRelatorios")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuCadastros.menuAction())
        self.menubar.addAction(self.menuLancamentos.menuAction())
        self.menubar.addAction(self.menuRelatorios.menuAction())
        self.menuCadastros.addAction(self.actionCad_Colaboradores)
        self.menuCadastros.addAction(self.actionSaldo_BIZ)
        self.menuCadastros.addAction(self.actionUsuarios)
        self.menuCadastros.addAction(self.actionCaminhoes)
        self.menuLancamentos.addAction(self.actionRecargas)
        self.menuRelatorios.addAction(self.actionRecarga_Colaborador)
        self.menuRelatorios.addAction(self.actionDash_Refeicao)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Controle de Recargas e Abastecimento", None))
        self.actionCad_Colaboradores.setText(QCoreApplication.translate("MainWindow", u"Colaboradores", None))
        self.actionRecargas.setText(QCoreApplication.translate("MainWindow", u"Recargas", None))
        self.actionSaldo_BIZ.setText(QCoreApplication.translate("MainWindow", u"Saldo BIZ", None))
        self.actionRecarga_Colaborador.setText(QCoreApplication.translate("MainWindow", u"Recarga por Colaborador", None))
        self.actionUsuarios.setText(QCoreApplication.translate("MainWindow", u"Usu\u00e1rios", None))
        self.actionDash_Refeicao.setText(QCoreApplication.translate("MainWindow", u"DashBoard Recargas", None))
        self.actionCaminhoes.setText(QCoreApplication.translate("MainWindow", u"Caminh\u00f5es", None))
        self.lb_Saldo_Conta.setText(QCoreApplication.translate("MainWindow", u"Saldo Conta:", None))
#if QT_CONFIG(tooltip)
        self.txt_Saldo_Conta.setToolTip(QCoreApplication.translate("MainWindow", u"Saldo da conta Biz (recargas - saldos)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.dt_Data_Atual.setToolTip(QCoreApplication.translate("MainWindow", u"Data de hoje", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.dt_Hora_Atual.setToolTip(QCoreApplication.translate("MainWindow", u"Hora atual", None))
#endif // QT_CONFIG(tooltip)
        self.lb_Versao.setText(QCoreApplication.translate("MainWindow", u"Vers\u00e3o 2.0.0", None))
        self.menuCadastros.setTitle(QCoreApplication.translate("MainWindow", u"Cadastros", None))
        self.menuLancamentos.setTitle(QCoreApplication.translate("MainWindow", u"Lan\u00e7amentos", None))
        self.menuRelatorios.setTitle(QCoreApplication.translate("MainWindow", u"Relat\u00f3rios", None))
    # retranslateUi

