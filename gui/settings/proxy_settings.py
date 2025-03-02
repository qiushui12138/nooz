import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QPushButton,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QMessageBox,
    QGroupBox,
)

from config.proxy_manager import proxy_manager


class ProxySettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading = False  # 添加加载标志
        self.setup_ui()
        self.setup_signals()
        self.load_saved_proxies()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 创建代理设置组
        proxy_group = QGroupBox("代理设置")
        proxy_group.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        layout = QVBoxLayout(proxy_group)
        layout.setSpacing(10)

        # 创建按钮组
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.add_btn = QPushButton("新增")
        self.delete_btn = QPushButton("删除")
        self.import_btn = QPushButton("导入")
        self.export_btn = QPushButton("导出")

        for btn in [self.add_btn, self.delete_btn, self.import_btn, self.export_btn]:
            btn.setMinimumWidth(80)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #2d2d2d;
                    border: 1px solid #3a3a3a;
                    border-radius: 4px;
                    padding: 5px 15px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:pressed {
                    background-color: #404040;
                }
            """
            )
            button_layout.addWidget(btn)
        button_layout.addStretch()

        # 创建搜索区域
        search_layout = QHBoxLayout()

        # 修改表格列数和标题
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(6)  # 增加到6列
        self.proxy_table.setHorizontalHeaderLabels(
            ["ADS_ID", "代理类型", "主机", "端口", "用户名", "密码"]
        )
        # 设置表格行高和头部高度
        self.proxy_table.verticalHeader().setDefaultSectionSize(40)  # 设置行高
        self.proxy_table.horizontalHeader().setFixedHeight(45)  # 设置表头高度

        # 设置表格样式
        self.proxy_table.setStyleSheet(
            """
                QTableWidget {
                    background-color: #2b2b2b;
                    border: 1px solid #3d3d3d;
                    border-radius: 6px;
                    gridline-color: #3d3d3d;
                }

                QTableWidget::item {
                    padding: 8px;
                    color: #e0e0e0;
                    border-bottom: 1px solid #3d3d3d;
                }

                QTableWidget::item:selected {
                    background-color: #345f80;
                    color: #ffffff;
                }

                QTableWidget::item:focus {
                    background-color: #345f80;
                    color: #ffffff;
                    border: none;
                }

                QHeaderView::section {
                    background-color: #232323;
                    color: #e0e0e0;
                    padding: 10px 8px;
                    border: none;
                    border-right: 1px solid #3d3d3d;
                    border-bottom: 2px solid #4a4a4a;
                    font-weight: bold;
                }

                QHeaderView::section:hover {
                    background-color: #2d2d2d;
                }

                QTableWidget::item:alternate {
                    background-color: #2f2f2f;
                }

                QTableWidget QLineEdit {
                    background-color: #333333;
                    color: #e0e0e0;
                    border: 1px solid #4a4a4a;
                    border-radius: 3px;
                    padding: 3px 6px;
                    selection-background-color: #345f80;
                }

                QScrollBar:vertical {
                    border: none;
                    background: #2b2b2b;
                    width: 10px;
                    margin: 0;
                }

                QScrollBar::handle:vertical {
                    background: #4a4a4a;
                    min-height: 30px;
                    border-radius: 5px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #555555;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0;
                }

                QScrollBar:horizontal {
                    border: none;
                    background: #2b2b2b;
                    height: 10px;
                    margin: 0;
                }

                QScrollBar::handle:horizontal {
                    background: #4a4a4a;
                    min-width: 30px;
                    border-radius: 5px;
                }

                QScrollBar::handle:horizontal:hover {
                    background: #555555;
                }

                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0;
                }
            """
        )

        # 设置表格属性
        self.proxy_table.setAlternatingRowColors(True)
        self.proxy_table.setShowGrid(True)
        self.proxy_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.proxy_table.horizontalHeader().setHighlightSections(False)
        self.proxy_table.verticalHeader().setHighlightSections(False)
        self.proxy_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.proxy_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.proxy_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.proxy_table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked
            | QTableWidget.EditTrigger.EditKeyPressed
            | QTableWidget.EditTrigger.AnyKeyPressed
        )

        # 添加组件到布局
        # 添加到布局
        layout.addLayout(button_layout)
        layout.addWidget(self.proxy_table)

        # 添加组到主布局
        main_layout.addWidget(proxy_group)

    def setup_signals(self):
        self.add_btn.clicked.connect(self.add_proxy)
        self.delete_btn.clicked.connect(self.delete_proxy)
        self.import_btn.clicked.connect(self.import_proxies)
        self.export_btn.clicked.connect(self.export_proxies)
        self.proxy_table.itemChanged.connect(self.on_item_changed)

    def load_saved_proxies(self):
        """加载保存的代理设置"""
        self._loading = True  # 开始加载
        try:
            proxies = proxy_manager.load_proxies()
            self.proxy_table.setRowCount(0)
            for proxy in proxies:
                row = self.proxy_table.rowCount()
                self.proxy_table.insertRow(row)
                for col, key in enumerate(
                    ["ads_id", "type", "host", "port", "username", "password"]
                ):
                    item = QTableWidgetItem(str(proxy.get(key, "")))
                    self.proxy_table.setItem(row, col, item)
        finally:
            self._loading = False  # 确保加载标志被重置

    def on_item_changed(self, item):
        """处理表格项变化"""
        if not self._loading:  # 只在非加载状态下保存
            self.save_proxies()

    def save_proxies(self):
        """保存代理设置到本地文件"""
        proxies = []
        for row in range(self.proxy_table.rowCount()):
            proxy = {
                "ads_id": (
                    self.proxy_table.item(row, 0).text()
                    if self.proxy_table.item(row, 0)
                    else ""
                ),
                "type": (
                    self.proxy_table.item(row, 1).text()
                    if self.proxy_table.item(row, 1)
                    else ""
                ),
                "host": (
                    self.proxy_table.item(row, 2).text()
                    if self.proxy_table.item(row, 2)
                    else ""
                ),
                "port": (
                    self.proxy_table.item(row, 3).text()
                    if self.proxy_table.item(row, 3)
                    else ""
                ),
                "username": (
                    self.proxy_table.item(row, 4).text()
                    if self.proxy_table.item(row, 4)
                    else ""
                ),
                "password": (
                    self.proxy_table.item(row, 5).text()
                    if self.proxy_table.item(row, 5)
                    else ""
                ),
            }
            # 只保存有效的代理（必须有广告ID和主机端口）
            if proxy["ads_id"] and proxy["host"] and proxy["port"]:
                proxies.append(proxy)

        if proxy_manager.save_proxies(proxies):
            print("代理设置已保存")
        else:
            QMessageBox.warning(self, "警告", "保存代理设置失败")

    def add_proxy(self):
        """添加新代理行"""
        row = self.proxy_table.rowCount()
        self.proxy_table.insertRow(row)
        for col in range(6):  # 修改为6列
            self.proxy_table.setItem(row, col, QTableWidgetItem(""))

    def delete_proxy(self):
        """删除选中的代理"""
        selected_rows = set(item.row() for item in self.proxy_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请选择要删除的行")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(selected_rows)} 行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):
                self.proxy_table.removeRow(row)

    def import_proxies(self):
        """从Excel导入代理"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入代理", "", "Excel 文件 (*.xlsx *.xls)"
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            if len(df.columns) != 6:
                raise ValueError("Excel格式不正确，需要6列数据")

            self._loading = True  # 开始导入
            try:
                # 清空现有数据
                self.proxy_table.setRowCount(0)

                # 导入新数据
                for _, row in df.iterrows():
                    table_row = self.proxy_table.rowCount()
                    self.proxy_table.insertRow(table_row)
                    for col, value in enumerate(row):
                        self.proxy_table.setItem(
                            table_row, col, QTableWidgetItem(str(value))
                        )
            finally:
                self._loading = False  # 确保加载标志被重置

            # 保存导入的代理
            self.save_proxies()
            QMessageBox.information(self, "成功", "代理导入成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def export_proxies(self):
        """导出代理到Excel"""
        if self.proxy_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出代理", "", "Excel 文件 (*.xlsx)"
        )
        if not file_path:
            return

        try:
            data = []
            for row in range(self.proxy_table.rowCount()):
                row_data = []
                for col in range(self.proxy_table.columnCount()):
                    item = self.proxy_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            df = pd.DataFrame(
                data, columns=["广告ID", "代理类型", "主机", "端口", "用户名", "密码"]
            )
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "成功", "代理导出成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
