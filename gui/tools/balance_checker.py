from typing import List

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class BalanceChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 创建按钮组
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("查询余额")
        self.check_button.clicked.connect(self.check_balances)
        button_layout.addWidget(self.check_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["地址", "0G", "Monad", "Sahara"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        layout.addWidget(self.table)

    def check_balances(self):
        """检查所有测试网余额"""
        # 从Excel数据中获取地址
        addresses = self.get_addresses_from_excel()
        if not addresses:
            return

        # 清空表格
        self.table.setRowCount(0)

        # 查询每个地址的余额
        for address in addresses:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # 设置地址
            self.table.setItem(row_position, 0, QTableWidgetItem(address))

            # 查询各个测试网余额
            balances = {
                "0G": self.get_0g_balance(address),
                "Monad": self.get_monad_balance(address),
                "Sahara": self.get_sahara_balance(address),
            }

            # 设置余额
            for col, (network, balance) in enumerate(balances.items(), 1):
                item = QTableWidgetItem(f"{balance:.4f}")
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self.table.setItem(row_position, col, item)

    def get_addresses_from_excel(self) -> List[str]:
        """从主窗口获取地址列表"""
        main_window = self.window()
        if hasattr(main_window, "excel_data"):
            return [row[1] for row in main_window.excel_data]  # 假设地址在第二列
        return []

    def get_0g_balance(self, address: str) -> float:
        """查询0G测试网余额"""
        try:
            response = requests.get(f"https://rpc.testnet.0g.ai/balance/{address}")
            if response.status_code == 200:
                return float(response.json().get("balance", 0)) / 1e18
        except Exception:
            pass
        return 0.0

    def get_monad_balance(self, address: str) -> float:
        """查询Monad测试网余额"""
        try:
            response = requests.get(f"https://rpc.testnet.monad.xyz/balance/{address}")
            if response.status_code == 200:
                return float(response.json().get("balance", 0)) / 1e18
        except Exception:
            pass
        return 0.0

    def get_sahara_balance(self, address: str) -> float:
        """查询Sahara测试网余额"""
        try:
            response = requests.get(f"https://rpc.testnet.sahara.ai/balance/{address}")
            if response.status_code == 200:
                return float(response.json().get("balance", 0)) / 1e18
        except Exception:
            pass
        return 0.0
