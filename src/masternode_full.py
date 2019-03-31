#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: zakurai
# Created on: 2019-05

import datetime, time
import logging
import math
from typing import List

from PyQt5.QtCore import Qt, pyqtSlot, QVariant
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QDialog, QTableView, QAbstractItemView

from app_config import MasternodeConfig, AppConfig
from dashd_intf import DashdInterface
from ext_item_model import ExtSortFilterTableModel, TableModelColumn
from ui import ui_masternode_full
import dash_utils
import wnd_utils

DATA_AGE=30

class MasternodeListTableModel(ExtSortFilterTableModel):
    def __init__(self, parent, app_config: AppConfig, all_mns: bool):
        columns = [
            TableModelColumn("ip_address", "IP Address", True, 100),
            TableModelColumn("protocol", "Protocol", True, 60),
            TableModelColumn("status", "Status", True, 100),
            TableModelColumn("activeseconds", "Active Time", True, 80),
            TableModelColumn("lastseen", "Last Seen", True, 80),
            TableModelColumn("payee_address", "Collateral Address", True, 120)
        ]
        if not all_mns:
            columns.insert(0, TableModelColumn("alias", "Name", True, 80))
        ExtSortFilterTableModel.__init__(self, parent, columns, True, True)
        wnd_utils.WndUtils.__init__(self, None)
        self.port = str(dash_utils.get_chain_params(app_config.dash_network).P2P_PORT)
        self.all = all_mns
        self.dashd_intf = parent.dashd_intf
        self.mnlist = app_config.masternodes
        self.parent = parent
        self.set_attr_protection()

    def get_mn_list(self):
        if not self.parent.my_fresh or not self.parent.all_fresh:
            if self.all:
                return self.dashd_intf.masternodes
            else:
                return self.mnlist
        else:
            return {}

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.get_mn_list())

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def set_view(self, table_view: QTableView):
        super().set_view(table_view)

    def data(self, index, role=None):
        if index.isValid():
            col_idx = index.column()
            row_idx = index.row()
            if role in (Qt.DisplayRole, Qt.EditRole, Qt.ForegroundRole):
                if row_idx < len(self.get_mn_list()):
                    mn = self.get_mn_list()[row_idx]
                    if mn:
                        if role in (Qt.DisplayRole, Qt.EditRole):
                            col = self.col_by_index(col_idx)
                            if col:
                                field_name = col.name
                                if not self.all:
                                    e = None
                                    if mn.collateralTx and mn.collateralTxIndex:
                                        e = self.dashd_intf.masternodes_by_ident.get(f"{mn.collateralTx}-{mn.collateralTxIndex}")
                                    if field_name == "alias":
                                        return mn.name if mn.name else ""
                                    elif field_name == "ip_address":
                                        return mn.ip if mn.ip else ""
                                    elif field_name == "protocol":
                                        return e.protocol if e is not None and e.protocol else ""
                                    elif field_name == "status":
                                        return e.status if e is not None and e.status else ""
                                    elif field_name == "activeseconds":
                                        return format_activeseconds(e.activeseconds) if e is not None and e.activeseconds else "00m:00s"
                                    elif field_name == "lastseen":
                                        return format_lastseen_time(e.lastseen) if e is not None and e.lastseen else ""
                                    elif field_name == "payee_address":
                                        return mn.collateralAddress if mn.collateralAddress else ""
                                else:
                                    if field_name == "ip_address":
                                        return mn.ip.replace(":" + self.port, "") if mn.ip else ""
                                    elif field_name == "protocol":
                                        return mn.protocol if mn.protocol else ""
                                    elif field_name == "status":
                                        return mn.status if mn.status else ""
                                    elif field_name == "activeseconds":
                                        return format_activeseconds(mn.activeseconds) if mn.activeseconds else "00m:00s"
                                    elif field_name == "lastseen":
                                        return format_lastseen_time(mn.lastseen) if mn.lastseen else ""
                                    elif field_name == "payee_address":
                                        return mn.payee if mn.payee else ""
                        elif role == Qt.ForegroundRole:
                            if self.rep_colour(mn):
                                return QColor(self.rep_colour(mn))
                            return QColor("black")
        return QVariant()

    def lessThan(self, col_index, left_row_index, right_row_index):
        col = self.col_by_index(col_index)
        if col:
            col_name = col.name
            get = False
            if not self.all:
                if col_name == "alias":         col_name = "name"
                if col_name == "ip_address":    col_name = "ip"
                if col_name == "payee_address": col_name = "collateralAddress"
                if col_name in ["protocol", "status", "activeseconds", "lastseen"]:
                    get = True
            else:
                if col_name == "ip_address":    col_name = "ip"
                if col_name == "payee_address": col_name = "payee"
            if 0 <= left_row_index < len(self.get_mn_list()) and 0 <= right_row_index < len(self.get_mn_list()):
                try:
                    if get:
                        left  = self.get_mn_list()[left_row_index]
                        right = self.get_mn_list()[right_row_index]
                        left_value  = self.dashd_intf.masternodes_by_ident.get(f"{left.collateralTx}-{left.collateralTxIndex}").__getattribute__(col_name)
                        right_value = self.dashd_intf.masternodes_by_ident.get(f"{right.collateralTx}-{right.collateralTxIndex}").__getattribute__(col_name)
                    else:
                        left_value  = self.get_mn_list()[left_row_index].__getattribute__(col_name)
                        right_value = self.get_mn_list()[right_row_index].__getattribute__(col_name)
                    if col_name == "ip":
                        left_ip  = left_value.replace(":" + self.port, "").split(".")
                        right_ip = right_value.replace(":" + self.port, "").split(".")
                        if len(left_ip) == 4 and len(right_ip) == 4:
                            for i in range(4):
                                if left_ip[i] != right_ip[i]:
                                    return int(left_ip[i]) < int(right_ip[i])
                    elif col_name == "status":
                        s = {
                            "REMOVE": 1,
                            "OUTPOINT_SPENT": 2,
                            "NEW_START_REQUIRED": 3,
                            "EXPIRED": 4,
                            "PRE_ENABLED": 5,
                            "WATCHDOG_EXPIRED": 6,
                            "ACTIVE": 7,
                            "ENABLED": 8
                        }
                        s_l = 0 if s.get(left_value)  is None else s.get(left_value)
                        s_r = 0 if s.get(right_value) is None else s.get(right_value)
                        return s_l < s_r
                    else:
                        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                            return left_value < right_value
                        elif isinstance(left_value, str) and isinstance(right_value, str):
                            return left_value.lower() < right_value.lower()
                except AttributeError:
                    return False
        return False

    def set_mn_stats(self, is_all: bool):
        def reset_stats():
            if is_all: self.parent.allMnStats = StatsObj()
            else:      self.parent.myMnStats  = StatsObj()
        def get_stats():
            if is_all: return self.parent.allMnStats
            else:      return self.parent.myMnStats
        reset_stats()
        for mn in self.get_mn_list():
            e = None
            if not is_all and mn.collateralTx and mn.collateralTxIndex:
                e = self.dashd_intf.masternodes_by_ident.get(f"{mn.collateralTx}-{mn.collateralTxIndex}")
            elif is_all:
                e = self.dashd_intf.masternodes_by_ident.get(mn.ident)
            if e is not None and e.status:
                if   e.status in ["ENABLED", "ACTIVE", "WATCHDOG_EXPIRED"]:
                    get_stats().enabled += 1
                elif e.status in ["PRE_ENABLED"]:
                    get_stats().pending += 1
                elif e.status in ["EXPIRED", "NEW_START_REQUIRED", "OUTPOINT_SPENT", "REMOVE"]:
                    get_stats().offline += 1
                else:
                    get_stats().unknown += 1
            else:   get_stats().unknown += 1

    def rep_colour(self, mn):
        key = None
        if not self.all:
            if (mn.collateralTx and mn.collateralTxIndex):
                key = f"{mn.collateralTx}-{mn.collateralTxIndex}"
            else:
                return "red"
        else:
            if mn.ident:
                key = mn.ident
            else:
                return "red"
        e = self.dashd_intf.masternodes_by_ident.get(key)
        if key is None or e is None or not e.status:
            return "red"
        if   e.status in ["ENABLED", "ACTIVE", "WATCHDOG_EXPIRED"]:
            return "green"
        elif e.status in ["PRE_ENABLED"]:
            return "blue"
        else:
            return "red"

class StatsObj:
    def __init__(self):
        self.enabled = 0
        self.pending = 0
        self.offline = 0
        self.unknown = 0

def format_activeseconds(rawtime):
    if not isinstance(rawtime, (int, float)):
        return ""
    days = rawtime / (24 * 60 * 60)
    hours = (days * 24) % 24
    mins = (hours * 60) % 60
    secs = (mins * 60) % 60
    result = ""
    if days >= 1:
        result += str(math.floor(days)) + "d "
    if days >= 1 or hours >= 1:
        if hours < 10: result += "0"
        result += str(math.floor(hours)) + "h:"
    if mins < 10: result += "0"
    result += str(math.floor(mins)) + "m:"
    if secs < 10: result += "0"
    result += str(math.floor(secs)) + "s"
    return result

def format_lastseen_time(rawtime):
    if not isinstance(rawtime, (int, float)):
        return ""
    d = datetime.datetime.fromtimestamp(rawtime)
    result = str(d.year) + "-"
    if d.month < 10: result += "0"
    result += str(d.month) + "-"
    if d.day < 10: result += "0"
    result += str(d.day) + " "
    if d.hour < 10: result += "0"
    result += str(d.hour) + ":"
    if d.minute < 10: result += "0"
    result += str(d.minute)
    return result

class MasternodeFull(QDialog, ui_masternode_full.Ui_MasternodeFull, wnd_utils.WndUtils):
    def __init__(self, main_ui, app_config: AppConfig):
        QDialog.__init__(self, parent=main_ui)
        wnd_utils.WndUtils.__init__(self, app_config)
        self.app_config = app_config
        self.dashd_intf: DashdInterface = main_ui.dashd_intf
        self.main_wnd = main_ui
        self.mymn_table_model  = MasternodeListTableModel(self, self.app_config, False)
        self.allmn_table_model = MasternodeListTableModel(self, self.app_config, True)
        self.my_fresh = True
        self.all_fresh = True
        self.currentTabIdx = 0
        self.refreshingTabIdx = 0
        self.myMnStats  = StatsObj()
        self.allMnStats = StatsObj()
        self.setupUi()

    def setupUi(self):
        ui_masternode_full.Ui_MasternodeFull.setupUi(self, self)
        self.update_tab_graphics()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.WindowMaximizeButtonHint)
        self.mymn_table_model.set_view(self.myMnsTable)
        self.allmn_table_model.set_view(self.allMnsTable)
        self.myMnsTable.setItemDelegate(wnd_utils.ReadOnlyTableCellDelegate(self.myMnsTable))
        self.allMnsTable.setItemDelegate(wnd_utils.ReadOnlyTableCellDelegate(self.allMnsTable))
        self.myMnsTable.verticalHeader().setDefaultSectionSize(self.myMnsTable.verticalHeader().fontMetrics().height() + 8)
        self.allMnsTable.verticalHeader().setDefaultSectionSize(self.allMnsTable.verticalHeader().fontMetrics().height() + 5)
        self.myMnsTable.horizontalHeader().setSortIndicator(self.mymn_table_model.col_index_by_name("status"), Qt.AscendingOrder)
        self.allMnsTable.horizontalHeader().setSortIndicator(self.allmn_table_model.col_index_by_name("lastseen"), Qt.DescendingOrder)
        self.snap_column_width()
        self.tabWidget.currentChanged.connect(self.on_tabWidget_currentChanged)

    def snap_column_width(self):
        for idx in range(self.mymn_table_model.col_count()):
            self.myMnsTable.resizeColumnToContents(idx)
            if self.myMnsTable.columnWidth(idx) < 90:
                self.myMnsTable.setColumnWidth(idx, 90)
        for idx in range(self.allmn_table_model.col_count()):
            self.allMnsTable.resizeColumnToContents(idx)
            if self.allMnsTable.columnWidth(idx) < 90:
                self.allMnsTable.setColumnWidth(idx, 90)

    def update_full_mn_list(self):
        def onFinish():
            self.snap_column_width()
            self.btnMasternodesFullRefresh.setEnabled(True)
            self.update_tab_graphics()
        
        def onExcept():
            onFinish()

        if self.refreshingTabIdx != 0 or len(self.app_config.masternodes) != 0:
            self.btnMasternodesFullRefresh.setEnabled(False)
            self.btnMasternodesFullRefresh.setStyleSheet("")
            self.setIcon(self.btnMasternodesFullRefresh, "")
            self.btnMasternodesFullRefresh.setText(" Fetching data... ")
            self.lblMasternodesFullMessage.setText("")
            self.main_wnd.connect_dash_network(wait_for_check_finish=True)
            if self.main_wnd.dashd_connection_ok:
                self.run_thread(self, self.update_list_thread, (), on_thread_finish=onFinish, on_thread_exception=onExcept)

        else:
            self.my_fresh = False
            onFinish()

    def update_list_thread(self, ctrl):
        if self.refreshingTabIdx == 0:
            self.my_fresh = False
            with self.mymn_table_model:
                self.dashd_intf.get_masternodelist("full", data_max_age=DATA_AGE)
                self.mymn_table_model.beginResetModel()
                self.mymn_table_model.endResetModel()
                self.mymn_table_model.set_mn_stats(False)
        elif self.refreshingTabIdx == 1:
            self.all_fresh = False
            with self.allmn_table_model:
                self.dashd_intf.get_masternodelist("full", data_max_age=DATA_AGE)
                self.allmn_table_model.beginResetModel()
                self.allmn_table_model.endResetModel()
                self.allmn_table_model.set_mn_stats(True)
                self.lblMasternodesFullCount.setText(f"Node Count: {len(self.dashd_intf.masternodes)}")

    def update_tab_graphics(self):
        if self.btnMasternodesFullRefresh.isEnabled():
            self.lblMasternodesFullMessage.setText("")
            if self.currentTabIdx == 0:
                if self.my_fresh:
                    self.btnMasternodesFullRefresh.setStyleSheet("font-weight:bold;")
                    self.btnMasternodesFullRefresh.setText("Fetch ")
                    self.setIcon(self.btnMasternodesFullRefresh, "arrow-downward@32px.png")
                else:
                    s = self.myMnStats
                    self.btnMasternodesFullRefresh.setStyleSheet("")
                    self.btnMasternodesFullRefresh.setText("Refresh ")
                    self.setIcon(self.btnMasternodesFullRefresh, "autorenew@16px.png")
                    self.lblMasternodesFullMessage.setText(construct_msg(s))
            elif self.currentTabIdx == 1:
                if self.all_fresh:
                    self.btnMasternodesFullRefresh.setStyleSheet("font-weight:bold;")
                    self.btnMasternodesFullRefresh.setText("Fetch all MNs ")
                    self.setIcon(self.btnMasternodesFullRefresh, "arrow-downward@32px.png")
                else:
                    s = self.allMnStats
                    self.btnMasternodesFullRefresh.setStyleSheet("")
                    self.btnMasternodesFullRefresh.setText("Refresh all MNs ")
                    self.setIcon(self.btnMasternodesFullRefresh, "autorenew@16px.png")
                    self.lblMasternodesFullMessage.setText(construct_msg(s))

    @pyqtSlot(int)
    def on_tabWidget_currentChanged(self, idx):
        self.currentTabIdx = idx
        self.update_tab_graphics()

    @pyqtSlot()
    def on_btnMasternodesFullRefresh_clicked(self):
        if self.btnMasternodesFullRefresh.isEnabled():
            self.refreshingTabIdx = self.currentTabIdx
            self.update_full_mn_list()

    @pyqtSlot()
    def on_buttonBox_rejected(self):
        self.reject()

def construct_msg(s):
    msg =  colour_if("green", "<b>Enabled:</b> ", s.enabled, False)
    msg += colour_if("blue",  "<b>Pending:</b> ", s.pending, True)
    msg += colour_if("red",   "<b>Offline:</b> ", s.offline, True)
    msg += colour_if("red",   "<b>Unknown:</b> ", s.unknown, True)
    return msg

def colour_if(colour, string, value, hide):
    if value > 0:
        return f"&nbsp;&nbsp;<span style=\"color:{colour}\">{string}{value}</span>"
    elif hide:
        return ""
    else:
        return f"{string}{value}"