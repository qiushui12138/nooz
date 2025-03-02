from datetime import datetime
from typing import Dict

import requests
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class GasMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gas_prices)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 创建控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始监控")
        self.start_button.clicked.connect(self.toggle_monitoring)
        self.update_button = QPushButton("立即更新")
        self.update_button.clicked.connect(self.update_gas_prices)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.update_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["网络", "低速", "中速", "高速"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(i, 100)

        # 预设行
        networks = ["Ethereum", "BSC", "Polygon", "Arbitrum", "Optimism", "Avalanche"]
        self.table.setRowCount(len(networks))
        for i, network in enumerate(networks):
            self.table.setItem(i, 0, QTableWidgetItem(network))

        layout.addWidget(self.table)

        # 添加更新时间显示
        self.update_time_label = QLabel("上次更新: 未更新")
        layout.addWidget(self.update_time_label)

    def toggle_monitoring(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("开始监控")
        else:
            self.timer.start(30000)  # 每30秒更新一次
            self.start_button.setText("停止监控")
            self.update_gas_prices()

    def update_gas_prices(self):
        try:
            # Ethereum
            eth_gas = self.get_ethereum_gas()
            self.update_row(0, eth_gas)

            # BSC
            bsc_gas = self.get_bsc_gas()
            self.update_row(1, bsc_gas)

            # Polygon
            polygon_gas = self.get_polygon_gas()
            self.update_row(2, polygon_gas)

            # Arbitrum
            arbitrum_gas = self.get_arbitrum_gas()
            self.update_row(3, arbitrum_gas)

            # Optimism
            optimism_gas = self.get_optimism_gas()
            self.update_row(4, optimism_gas)

            # Avalanche
            avalanche_gas = self.get_avalanche_gas()
            self.update_row(5, avalanche_gas)

            # 更新时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.update_time_label.setText(f"上次更新: {current_time}")

        except Exception as e:
            print(f"更新gas价格失败: {str(e)}")

    def update_row(self, row: int, gas_data: Dict[str, float]):
        for col, key in enumerate(["low", "medium", "high"], 1):
            if gas_data.get(key) is not None:
                item = QTableWidgetItem(f"{gas_data[key]:.2f}")
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self.table.setItem(row, col, item)

    def get_ethereum_gas(self) -> Dict[str, float]:
        response = requests.get(
            "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
        )
        data = response.json()
        return {
            "low": float(data["result"]["SafeLow"]),
            "medium": float(data["result"]["ProposeGas"]),
            "high": float(data["result"]["FastGas"]),
        }

    def get_bsc_gas(self) -> Dict[str, float]:
        response = requests.get(
            "https://api.bscscan.com/api?module=gastracker&action=gasoracle"
        )
        data = response.json()
        return {
            "low": float(data["result"]["SafeLow"]),
            "medium": float(data["result"]["ProposeGas"]),
            "high": float(data["result"]["FastGas"]),
        }

    def get_polygon_gas(self) -> Dict[str, float]:
        response = requests.get(
            "https://api.polygonscan.com/api?module=gastracker&action=gasoracle"
        )
        data = response.json()
        return {
            "low": float(data["result"]["SafeLow"]),
            "medium": float(data["result"]["ProposeGas"]),
            "high": float(data["result"]["FastGas"]),
        }

    def get_arbitrum_gas(self) -> Dict[str, float]:
        response = requests.get(
            "https://api.arbiscan.io/api?module=gastracker&action=gasoracle"
        )
        data = response.json()
        return {
            "low": float(data["result"]["SafeLow"]),
            "medium": float(data["result"]["ProposeGas"]),
            "high": float(data["result"]["FastGas"]),
        }

    def get_optimism_gas(self) -> Dict[str, float]:
        response = requests.get(
            "https://api-optimistic.etherscan.io/api?module=gastracker&action=gasoracle"
        )
        data = response.json()
        return {
            "low": float(data["result"]["SafeLow"]),
            "medium": float(data["result"]["ProposeGas"]),
            "high": float(data["result"]["FastGas"]),
        }

    def get_avalanche_gas(self) -> Dict[str, float]:
        response = requests.get(
            "https://api.snowtrace.io/api?module=gastracker&action=gasoracle"
        )
        data = response.json()
        return {
            "low": float(data["result"]["SafeLow"]),
            "medium": float(data["result"]["ProposeGas"]),
            "high": float(data["result"]["FastGas"]),
        }
