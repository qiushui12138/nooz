from datetime import datetime
from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QPushButton,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class LogGroup(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("运行日志", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # 创建主容器
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["时间", "级别", "内容"])
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setSortingEnabled(True)

        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.export_btn = QPushButton("导出日志到Excel")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.log_table)
        layout.addWidget(self.export_btn)

    def add_log_entry(self, timestamp, level, message):
        """添加日志条目"""
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        # 设置时间
        dt = datetime.fromtimestamp(timestamp)
        time_item = QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S"))
        self.log_table.setItem(row, 0, time_item)

        # 设置级别和颜色
        level_item = QTableWidgetItem(level)
        if level == "ERROR":
            level_item.setForeground(QColor("#e74c3c"))
        elif level == "WARNING":
            level_item.setForeground(QColor("#f39c12"))
        elif level == "SUCCESS":
            level_item.setForeground(QColor("#2ecc71"))
        self.log_table.setItem(row, 1, level_item)

        # 设置消息内容
        message_item = QTableWidgetItem(str(message))
        self.log_table.setItem(row, 2, message_item)

        # 滚动到最新的日志
        self.log_table.scrollToBottom()
