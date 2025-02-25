from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtGui import QIcon


class FileGroup(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("文件管理", parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.import_btn = QPushButton("导入 Excel 文件")
        self.import_btn.setIcon(QIcon.fromTheme("document-open"))
        self.file_label = QLabel("未选择文件")

        layout.addWidget(self.import_btn)
        layout.addWidget(self.create_horizontal_line())
        layout.addWidget(self.file_label)
        self.setLayout(layout)

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
