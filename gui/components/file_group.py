from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal
import pandas as pd
import os


class FileGroup(QGroupBox):
    # 定义信号
    excel_loaded = pyqtSignal(list, int)  # 数据, 总行数

    def __init__(self, parent=None):
        super().__init__("文件管理", parent)
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.import_btn = QPushButton("导入 Excel 文件")
        self.import_btn.setIcon(QIcon.fromTheme("document-open"))
        self.file_label = QLabel("未选择文件")

        layout.addWidget(self.import_btn)
        layout.addWidget(self.create_horizontal_line())
        layout.addWidget(self.file_label)
        self.setLayout(layout)

    def setup_signals(self):
        self.import_btn.clicked.connect(self.import_excel)

    def create_horizontal_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def disable_controls(self):
        """禁用所有控件"""
        self.import_btn.setEnabled(False)

    def enable_controls(self):
        """启用所有控件"""
        self.import_btn.setEnabled(True)

    def import_excel(self):
        """导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Excel 文件", "", "Excel 文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.load_excel_data(file_path)

    def load_excel_data(self, file_path: str):
        """加载Excel数据"""
        file_path = os.path.normpath(os.path.abspath(file_path))
        if not os.path.isfile(file_path):
            self.show_error("文件不存在")
            return

        try:
            sheets = pd.ExcelFile(file_path).sheet_names
            sheet_name, ok = QInputDialog.getItem(
                self, "选择工作表", "请选择工作表:", sheets, 0, False
            )
            if ok and sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                data = df.iloc[:, :3].dropna().values.tolist()
                self.file_label.setText(f"已加载: {os.path.basename(file_path)}")
                self.excel_loaded.emit(data, len(data))

        except FileNotFoundError:
            self.show_error("文件未找到")
        except pd.errors.EmptyDataError:
            self.show_error("Excel文件为空")
        except Exception as e:
            self.show_error(f"未知错误: {str(e)}")

    def show_error(self, message: str):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)
