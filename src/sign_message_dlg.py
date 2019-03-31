#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Bertrand256
# Created on: 2017-04

import base64
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import wnd_utils as wnd_utils
import hw_intf
from app_defs import HWType
from common import CancelException
from ui import ui_sign_message_dlg
import logging


class SignMessageDlg(QDialog, ui_sign_message_dlg.Ui_SignMessageDlg, wnd_utils.WndUtils):
    def __init__(self, main_ui, hw_session, bip32path, address):
        QDialog.__init__(self, parent=main_ui)
        self.hw_session = hw_session
        self.bip32path = bip32path
        self.address = address
        self.setupUi()

    def setupUi(self):
        ui_sign_message_dlg.Ui_SignMessageDlg.setupUi(self, self)
        self.setWindowTitle('Sign message')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.btnSignMessage.clicked.connect(self.btnSignMessageClick)
        self.btnClose.clicked.connect(self.close)
        self.edtSigningAddress.setText(self.address)
        self.edtSignedMessage.setWordWrapMode(3)

    def btnSignMessageClick(self):
        try:
            msg_to_sign = self.edtMessageToSign.toPlainText()
            if msg_to_sign:
                # for ledger HW check if the message contains non-ascii characters
                if self.hw_session.app_config.hw_type == HWType.ledger_nano_s:
                    try:
                        msg_to_sign.encode('ascii')
                    except UnicodeEncodeError:
                        if len(msg_to_sign) > 140:
                            self.warnMsg('Ledger wallets cannot sign non-ASCII and non-printable characters, and cannot'
                                     'sign more than 140 characters. Please change your message and try again.')
                        else:
                            self.warnMsg('Ledger wallets cannot sign non-ASCII and non-printable characters. Please '
                                     'remove them from your message and try again.')
                        return
                    if len(msg_to_sign) > 140:
                        self.warnMsg('Ledger wallets cannot sign messages longer than 140 characters. Please '
                                     'remove any extra characters and try again.')
                        return

                sig = hw_intf.hw_sign_message(self.hw_session, self.bip32path, msg_to_sign)
                signed = base64.b64encode(sig.signature)
                # hex_message = binascii.hexlify(sig.signature).decode('base64')
                self.edtSignedMessage.setPlainText(signed.decode('ascii'))
                if sig.address != self.address:
                    self.warnMsg('The message was signed, but the signing address for the BIP32 path (%s) differs from the one '
                                 'you intended.\n\nMaybe you entered a bad passphrase, and are not using the correct device for the current config?\n\n'
                                 'Intended: %s\nActual: %s' % (self.bip32path, self.address, sig.address))
            else:
                self.errorMsg('Empty message cannot be signed.')

        except CancelException:
            logging.warning('CancelException')

        except Exception as e:
            logging.exception('Sign message exception:')
            self.errorMsg(str(e))

