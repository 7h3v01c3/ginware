#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Bertrand256
# Created on: 2017-05
import datetime
import json
import logging

import re
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QDialogButtonBox
import wnd_utils as wnd_utils
from app_config import DATE_FORMAT, DATETIME_FORMAT
from dashd_intf import DashdIndexException
from ui import ui_proposals
from src.common import AttrsProtected
from src.wnd_utils import WndUtils


class ProposalColumn(AttrsProtected):
    def __init__(self, symbol, caption, visible, voting_mn=None):
        """
        Constructor.
        :param symbol: Column symbol/name. There are a) static columns, which name carries information about
            column destinations (these columns are defined in PROPOSAL_COLUMNS) and b) dynamic columns, which
            present voting made by specified masternodes for each proposal.
        :param caption: The column's caption.
        :param visible: True, if column is visible
        :param voting_mn: Used only when the column is dynamic (otherwise the value is None). In this case, the
            value should be the masternode's ident, which comprises of masternode's collateral transaction hash
            and the transaction index, separated by dash character (-).
        """
        AttrsProtected.__init__(self)
        self.symbol = symbol
        self.caption = caption
        self.visible = visible
        self.voting_mn = voting_mn
        self.set_attr_protection()


class ProposalVotingColumn(AttrsProtected):
    def __init__(self, mn_ident, column_caption, proposal_attr_name):
        """
        Information about grid's columns presenting results of user-selected masternodes
        voting.
        """
        AttrsProtected.__init__(self)
        self.mn_ident = mn_ident
        self.column_caption = column_caption
        self.proposal_attr_name = proposal_attr_name
        self.set_attr_protection()


PROPOSAL_COLUMNS = [
    ProposalColumn('name', 'Name', True),
    ProposalColumn('payment_start', 'Payment start', True),
    ProposalColumn('payment_end', 'Payment end', True),
    ProposalColumn('payment_amount', 'Amount', True),
    ProposalColumn('yes_count', 'Yes count', True),
    ProposalColumn('no_count', 'No count', True),
    ProposalColumn('abstain_count', 'Abstain count', True),
    ProposalColumn('creation_time', 'Creation time', True),
    ProposalColumn('url', 'URL', True),
    ProposalColumn('payment_address', 'Payment address', True),
    ProposalColumn('hash', 'Hash', True),
    ProposalColumn('collateral_hash', 'Collateral hash', True),
    ProposalColumn('fCachedDelete', 'fCachedDelete', True),
    ProposalColumn('fCachedFunding', 'fCachedFunding', True),
    ProposalColumn('fCachedEndorsed', 'fCachedEndorsed', True),
    ProposalColumn('ObjectType', 'ObjectType', True),
    ProposalColumn('fBlockchainValidity', 'fBlockchainValidity', True),
    ProposalColumn('IsValidReason', 'IsValidReason', True)
]


class Vote(AttrsProtected):
    def __init__(self, voting_masternode, vote_time, vote_result):
        super().__init__()
        self.voting_masternode = voting_masternode
        self.vote_time = vote_time
        self.vote_result = vote_result
        self.set_attr_protection()


class Proposal(object):
    def __init__(self):
        self.voting_loaded = False
        self.visible = True
        self.votes = []

    def add_vote(self, vote):
        self.votes.append(vote)

    def __getattr__(self, name):
        for pc in PROPOSAL_COLUMNS:
            if pc.symbol == name:
                return super().__getattr__(name)
        raise AttributeError('Attribute "%s" not found in the "Proposal" object.' % name)

    def __setattr__(self, name, value):
        if name in ('voting_loaded', 'visible', 'votes'):
            super().__setattr__(name, value)
        else:
            for pc in PROPOSAL_COLUMNS:
                if pc.symbol == name:
                    super().__setattr__(name, value)
                    return
            raise AttributeError('Attribute "%s" not found in the "Proposal" object.' % name)


class ProposalsDlg(QDialog, ui_proposals.Ui_ProposalsDlg, wnd_utils.WndUtils):
    def __init__(self, parent, dashd_intf):
        QDialog.__init__(self, parent=parent)
        wnd_utils.WndUtils.__init__(self, app_path=parent.app_path)
        self.main_wnd = parent
        self.dashd_intf = dashd_intf
        self.proposals = []
        self.masternodes_by_ident = {}
        self.mn_count = None
        self.setupUi()

    def setupUi(self):
        try:
            ui_proposals.Ui_ProposalsDlg.setupUi(self, self)
            self.setWindowTitle('Proposals')

            # let's define "dynamic" columns, showing voting results for user-specified masternodes
            for idx, mn in enumerate(self.main_wnd.config.masternodes):
                mn_ident = mn.collateralTx + '-' + str(mn.collateralTxIndex)
                if mn_ident:
                    mn_label = mn.name
                    attr_value_name = 'mn_voting_' + str(idx)
                    PROPOSAL_COLUMNS.append(ProposalColumn(attr_value_name,
                                                           'Voting (' + mn_label + ')', True,
                                                            voting_mn=mn_ident))

            # setup proposals grid
            self.tableWidget.clear()
            self.tableWidget.setColumnCount(len(PROPOSAL_COLUMNS))
            for idx, col in enumerate(PROPOSAL_COLUMNS):
                item = QtWidgets.QTableWidgetItem()
                item.setText(col.caption)
                self.tableWidget.setHorizontalHeaderItem(idx, item)
                if not col.visible:
                    self.tableWidget.hideColumn(idx)

            self.lblMessage.setVisible(True)
            self.lblMessage.setText('<b style="color:orange">Reading proposals data, please wait...<b>')
            self.runInThread(self.load_proposals_thread, (), self.display_data)
            self.updateUi()
        except:
            logging.exception('Exception occurred')
            raise

    def updateUi(self):
        items = self.tableWidget.selectedItems()
        selected = len(items) > 0
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(selected)

    def column_index_by_name(self, name):
        """
        Returns index of a column with a given name.
        :param name: name of a column
        :return: index of a column
        """
        for idx, pc in enumerate(PROPOSAL_COLUMNS):
            if pc.symbol == name:
                return idx
        raise Exception('Invalid proposal column name: ' + name)

    def load_proposals_thread(self, ctrl):
        def find_prop_data(prop_data, level=1):
            """
            Find proposal dict inside a list extracted from DataString field
            """
            if isinstance(prop_data, list):
                if len(prop_data) > 2:
                    logging.warning('len(prop_data) > 2 [level: %d]. prop_data: %s' % (level, json.dumps(prop_data)))

                if len(prop_data) >= 2 and prop_data[0] == 'proposal' and isinstance(prop_data[1], dict):
                    return prop_data[1]
                elif len(prop_data) >= 1 and isinstance(prop_data[0], list):
                    return find_prop_data(prop_data[0], level+1)
            return None

        try:
            if not self.dashd_intf.open():
                self.errorMsg('Dash daemon not connected')
            else:
                try:
                    # get list of all masternodes
                    mns = self.dashd_intf.get_masternodelist('full')
                    self.mn_count = 0
                    statuses = {}
                    # count all active masternodes
                    for mn in mns:
                        if mn.status in ('ENABLED','PRE_ENABLED','NEW_START_REQUIRED','WATCHDOG_EXPIRED'):
                            self.mn_count += 1
                        if statuses.get(mn.status):
                            statuses[mn.status] += 1
                        else:
                            statuses[mn.status] = 1

                        # add mn to an ident indexed dict
                        self.masternodes_by_ident[mn.ident] = mn

                    proposals = self.dashd_intf.gobject("list", "valid", "proposals")
                    for pro_key in proposals:
                        prop_raw = proposals[pro_key]

                        prop_dstr = prop_raw.get("DataString")
                        prop_data_json = json.loads(prop_dstr)
                        prop_data = find_prop_data(prop_data_json)
                        if prop_data is None:
                            continue

                        prop = Proposal()
                        prop.name = prop_data['name']
                        prop.hash = prop_raw['Hash']
                        prop.collateral_hash = prop_raw['CollateralHash']
                        prop.payment_start = datetime.datetime.fromtimestamp(int(prop_data['start_epoch']))
                        prop.payment_end = datetime.datetime.fromtimestamp(int(prop_data['end_epoch']))
                        prop.payment_amount = float(prop_data['payment_amount'])
                        prop.yes_count = int(prop_raw['YesCount'])
                        prop.no_count = int(prop_raw['NoCount'])
                        prop.abstain_count = int(prop_raw['AbstainCount'])
                        prop.creation_time = datetime.datetime.fromtimestamp(int(prop_raw["CreationTime"]))
                        prop.url = prop_data['url']
                        prop.payment_address = prop_data["payment_address"]
                        prop.fCachedDelete = prop_raw['fCachedDelete']
                        prop.fCachedFunding = prop_raw['fCachedFunding']
                        prop.fCachedEndorsed = prop_raw['fCachedEndorsed']
                        prop.ObjectType = prop_raw['ObjectType']
                        prop.fBlockchainValidity = prop_raw['fBlockchainValidity']
                        prop.IsValidReason = prop_raw['IsValidReason']
                        self.proposals.append(prop)

                    self.runInThread(self.read_voting_results_thread, (False,))
                except DashdIndexException as e:
                    self.errorMsg(str(e))

                except Exception as e:
                    logging.exception('Exception while retrieving proposals data.')
                    self.errorMsg('Error while retrieving proposals data: ' + str(e))
        except Exception as e:
            pass

    def read_voting_results_thread(self, ctrl, force_reload):
        """
        Retrieve from a Dash daemon voting results for all defined masternodes, for all visible Proposals.
        :param ctrl:
        :param force_reload: if False (default) we read voting results only for Proposals, which hasn't
          been read yet (for example has been filtered out).
        :return:
        """
        def display_voting_data():
            pass

        try:
            if not self.dashd_intf.open():
                self.errorMsg('Dash daemon not connected')
            else:
                try:
                    for prop in self.proposals:
                        if prop.visible and (not prop.voting_loaded or force_reload):
                            votes = self.dashd_intf.gobject("getvotes", prop.hash)
                            for v_key in votes:
                                v = votes[v_key]
                                match = re.search("CTxIn\(COutPoint\(([A-Fa-f0-9]+)\s*\,\s*(\d+).+\:(\d+)\:(\w+)", v)
                                if len(match.groups()) == 4:
                                    mn_ident = match.group(1) + '-' + match.group(2)
                                    voting_time = datetime.datetime.fromtimestamp(int(match.group(3)))
                                    voting_result = match.group(4)
                                    mn = self.masternodes_by_ident.get(mn_ident)
                                    if mn:
                                        v = Vote(mn, voting_time, voting_result)
                                        prop.add_vote(v)

                                    # check if voting masternode has its column in the main grid's;
                                    # if so, pass the voting result to a corresponding proposal field
                                    for col_idx, col in enumerate(PROPOSAL_COLUMNS):
                                        if col.voting_mn == mn_ident:
                                            setattr(prop, col.symbol, voting_result)
                                            break
                                else:
                                    logging.warning('Proposal %s, parsing unsuccessful for voting: %s' % (prop.hash, v))
                    # display data from dynamict (voting) columns
                    WndUtils.callFunInTheMainThread(display_voting_data)

                except DashdIndexException as e:
                    self.errorMsg(str(e))

                except Exception as e:
                    logging.exception('Exception while retrieving voting data.')
                    self.errorMsg('Error while retrieving voting data: ' + str(e))
        except Exception as e:
            pass

    def display_data(self):
        def item(value, horz_align = None):
            if isinstance(value, (int, float)):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, value)
            else:
                item = QTableWidgetItem(str(value))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if horz_align:
                item.setTextAlignment(horz_align)

            return item

        """
        'AbsoluteYesCount' = {int} 1233
        'AbstainCount' = {int} 5
        'CollateralHash' = {str} '8a7c9db293aeccf205b026753e12f57043f62b989ae0b0bfbbf467a3078e83ac'
        'CreationTime' = {int} 1487539972
        'DataHex' = {str} '
        'DataString' = {str} 
        '   [
               [
                  "proposal",
                  {
                     "end_epoch":"1495164424",
                     "name":"dash-detailed-2-shows",
                     "payment_address":"XbXb6rUeDrPcCe9xyoGTBL7TDkBU46KTvv",
                     "payment_amount":"215",
                     "start_epoch":"1487437984",
                     "type":1,
                     "url":"https://www.dash.org/forum/threads/dash-detailed-investor-report-5-pre-proposal.13136/"
                  }
               ]
            }
        '
        'Hash' = {str} '039db789f67dc8cddaddc5a382d805615da9298cd6a14620aa4ef81fd5d96430'
        'IsValidReason' = {str} ''
        'NoCount' = {int} 66
        'ObjectType' = {int} 1
        'YesCount' = {int} 1299
        'fBlockchainValidity' (5845426440) = {bool} True
        'fCachedDelete' (5845347568) = {bool} False
        'fCachedEndorsed' (5845347632) = {bool} False
        'fCachedFunding' (5845347504) = {bool} True
        'fCachedValid' (5845347440) = {bool} True"""

        """
        active:
        __len__ = {int} 16
        'AbsoluteYesCount' (5856492976) = {int} 404
        'AbstainCount' (5856443248) = {int} 3
        'CollateralHash' (5856442480) = {str} '4aee1851eeec5af3005b61fcc76d076269dffed004ea93d183957dd8000e6b9c'
        'CreationTime' (5856443184) = {int} 1494078194
        'DataHex' (5856434976) = {str} '5b5b2270726f706f73616c222c7b22656e645f65706f6368223a2231343937383435363234222c226e616d65223a224372656174652d7468652d66697273742d444153482d676174657761792d6f6e2d526970706c65222c227061796d656e745f61646472657373223a22587269416333564333793479617974686f46795a3
        'DataString' (4692987184) = {str} '[["proposal",{"end_epoch":"1497845624","name":"Create-the-first-DASH-gateway-on-Ripple","payment_address":"XriAc3VC3y4yaythoFyZ3YLRo1waumTdoB","payment_amount":"150","start_epoch":"1495270144","type":1,"url":"https://www.dashcentral.org/p/Create-the-first
        'Hash' (5856434696) = {str} '8a1d4e8f881d54d9314dc0d081f045cf74b187f8527ad763a11e101381226939'
        'IsValidReason' (5856443312) = {str} ''
        'NoCount' (5856435480) = {int} 50
        'ObjectType' (5856441776) = {int} 1
        'YesCount' (5856443120) = {int} 454
        'fBlockchainValidity' (5856493048) = {bool} True
        'fCachedDelete' (5856443440) = {bool} False
        'fCachedEndorsed' (5856443632) = {bool} False
        'fCachedFunding' (5856443504) = {bool} False
        'fCachedValid' (5856443568) = {bool} True        
        """

        try:
            row = 0

            for prop in self.proposals:
                # if prop.get('fCachedFunding', False) or prop.get('fCachedEndorsed', False):
                #     continue
                self.tableWidget.insertRow(self.tableWidget.rowCount())

                # "name" column display as a hyperlink if possible
                if prop.url:
                    url_lbl = QtWidgets.QLabel(self.tableWidget)
                    url_lbl.setText('<a href="%s">%s</a>' % (prop.url, prop.name))
                    url_lbl.setOpenExternalLinks(True)
                    self.tableWidget.setCellWidget(row, self.column_index_by_name('name'), url_lbl)
                else:
                    self.tableWidget.setItem(row, self.column_index_by_name('name'), prop.name)

                self.tableWidget.setItem(row, self.column_index_by_name('hash'), item(prop.hash))
                self.tableWidget.setItem(row, self.column_index_by_name('collateral_hash'), item(prop.collateral_hash))
                self.tableWidget.setItem(row, self.column_index_by_name('payment_start'), item(prop.payment_start))
                self.tableWidget.setItem(row, self.column_index_by_name('payment_end'), item(prop.payment_end))
                self.tableWidget.setItem(row, self.column_index_by_name('payment_amount'), item(prop.payment_amount, Qt.AlignRight))
                self.tableWidget.setItem(row, self.column_index_by_name('yes_count'), item(prop.yes_count, Qt.AlignRight))
                self.tableWidget.setItem(row, self.column_index_by_name('no_count'), item(prop.no_count, Qt.AlignRight))
                self.tableWidget.setItem(row, self.column_index_by_name('abstain_count'), item(prop.abstain_count, Qt.AlignRight))
                self.tableWidget.setItem(row, self.column_index_by_name('creation_time'), item(prop.creation_time))

                if prop.url:
                    url_lbl = QtWidgets.QLabel(self.tableWidget)
                    url_lbl.setText('<a href="%s">%s</a>' % (prop.url, prop.url))
                    url_lbl.setOpenExternalLinks(True)
                    self.tableWidget.setCellWidget(row, self.column_index_by_name('url'), url_lbl)
                else:
                    self.tableWidget.setItem(row, self.column_index_by_name('url'), prop.url)

                self.tableWidget.setItem(row, self.column_index_by_name('payment_address'), item(prop.payment_address))
                self.tableWidget.setItem(row, self.column_index_by_name('fCachedDelete'), item(prop.fCachedDelete))
                self.tableWidget.setItem(row, self.column_index_by_name('fCachedFunding'), item(prop.fCachedFunding))
                self.tableWidget.setItem(row, self.column_index_by_name('fCachedEndorsed'), item(prop.fCachedEndorsed))
                self.tableWidget.setItem(row, self.column_index_by_name('ObjectType'), item(prop.ObjectType))
                self.tableWidget.setItem(row, self.column_index_by_name('fBlockchainValidity'), item(prop.fBlockchainValidity))
                self.tableWidget.setItem(row, self.column_index_by_name('IsValidReason'), item(prop.IsValidReason))

                row += 1

            self.tableWidget.resizeColumnsToContents()
            self.lblMessage.setVisible(False)
            self.centerByWindow(self.main_wnd)

        except Exception as e:
            logging.exception("Exception occurred while displaing proposals.")
            self.lblMessage.setVisible(False)
            raise Exception('Error occurred while displaying proposals: ' + str(e))


            # self.tableWidget.setItem(row, 1, item(str(utxo.get('outputIndex', None))))
            # self.tableWidget.setItem(row, 2, item(utxo.get('time_str', None)))
            # self.tableWidget.setItem(row, 3, item(str(self.block_count - utxo.get('height', 0))))
        #
        # if len(self.utxos):
        #     self.tableWidget.resizeColumnsToContents()
        #     sh = self.sizeHint()
        #     sh.setWidth(sh.width() + 30)
        #     if sh.height() < 300:
        #         sh.setHeight(300)
        #     if sh.width() < 700:
        #         sh.setWidth(700)
        #     self.setBaseSize(sh)
        #     self.lblMessage.setVisible(False)
        #     self.centerByWindow(self.main_wnd)
        # else:
        #     self.lblMessage.setText('<b style="color:red">Found no unspent transactions with 1000 Dash '
        #                             'amount sent to address %s.<b>' %
        #                             self.dash_address)
        #     self.lblMessage.setVisible(True)

        self.updateUi()

    @pyqtSlot()
    def on_buttonBox_accepted(self):
        self.accept()

    @pyqtSlot()
    def on_buttonBox_rejected(self):
        self.reject()

    @pyqtSlot()
    def on_tableWidget_itemSelectionChanged(self):
        self.updateUi()

