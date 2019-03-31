# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about_dlg.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDlg(object):
    def setupUi(self, AboutDlg):
        AboutDlg.setObjectName("AboutDlg")
        AboutDlg.resize(617, 327)
        AboutDlg.setMinimumSize(QtCore.QSize(617, 327))
        AboutDlg.setMaximumSize(QtCore.QSize(617, 327))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(AboutDlg)
        self.verticalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_13.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_13.setSpacing(3)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_13.addLayout(self.verticalLayout)
        self.frame = QtWidgets.QFrame(AboutDlg)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setContentsMargins(0, 6, 6, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lblImage = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblImage.sizePolicy().hasHeightForWidth())
        self.lblImage.setSizePolicy(sizePolicy)
        self.lblImage.setMinimumSize(QtCore.QSize(64, 64))
        self.lblImage.setMaximumSize(QtCore.QSize(64, 64))
        self.lblImage.setText("")
        self.lblImage.setObjectName("lblImage")
        self.verticalLayout_3.addWidget(self.lblImage, 0, QtCore.Qt.AlignHCenter)
        self.lblAppName = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lblAppName.setFont(font)
        self.lblAppName.setObjectName("lblAppName")
        self.verticalLayout_3.addWidget(self.lblAppName, 0, QtCore.Qt.AlignHCenter)
        self.textAbout = QtWidgets.QTextBrowser(self.frame)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.textAbout.setFont(font)
        self.textAbout.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textAbout.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.textAbout.setObjectName("textAbout")
        self.verticalLayout_3.addWidget(self.textAbout)
        self.horizontalLayout_13.addWidget(self.frame)
        self.horizontalLayout_13.setStretch(1, 5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_13)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnClose = QtWidgets.QPushButton(AboutDlg)
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout.addWidget(self.btnClose)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(AboutDlg)
        QtCore.QMetaObject.connectSlotsByName(AboutDlg)

    def retranslateUi(self, AboutDlg):
        _translate = QtCore.QCoreApplication.translate
        AboutDlg.setWindowTitle(_translate("AboutDlg", "Dialog"))
        self.lblAppName.setText(_translate("AboutDlg", "GINware"))
        self.textAbout.setHtml(_translate("AboutDlg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">GINware is based on the fantastic Dash Masternode Tool (DMT) by Bertrand256.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">It is free for commercial and non-commercial use and is released as an open source project.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">- GINware -</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">GitHub:</span><span style=\" font-size:10pt;\"> </span><a href=\"https://github.com/GIN-coin/ginware\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">https://github.com/GIN-coin/ginware</span></a></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Maintainer:</span><span style=\" font-size:10pt;\"> zakurai (</span><a href=\"mailto:zakurai@pm.me\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">zakurai@pm.me</span></a><span style=\" font-size:10pt;\">)</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">- DMT -</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">GitHub:</span><span style=\" font-size:10pt;\"> </span><a href=\"https://github.com/Bertrand256/dash-masternode-tool\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">https://github.com/Bertrand256/dash-masternode-tool</span></a></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Author:</span><span style=\" font-size:10pt;\"> Bertrand256 (</span><a href=\"mailto:blogin@protonmail.com\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">blogin@protonmail.com</span></a><span style=\" font-size:10pt;\">)</span></p></body></html>"))
        self.btnClose.setText(_translate("AboutDlg", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AboutDlg = QtWidgets.QDialog()
    ui = Ui_AboutDlg()
    ui.setupUi(AboutDlg)
    AboutDlg.show()
    sys.exit(app.exec_())

