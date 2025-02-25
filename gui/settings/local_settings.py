from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QGroupBox,
)
import json
import os


class LocalSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_tasks_config()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 创建任务配置组
        config_group = QGroupBox("任务配置")
        config_group.setStyleSheet(
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

        layout = QVBoxLayout(config_group)
        layout.setSpacing(10)

        # 创建文本编辑器
        self.config_editor = QPlainTextEdit()
        self.config_editor.setReadOnly(True)
        self.config_editor.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """
        )

        layout.addWidget(self.config_editor)
        main_layout.addWidget(config_group)

    def load_tasks_config(self):
        """加载任务配置文件"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "tasks.json",
            )
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                # 格式化 JSON 显示
                formatted_json = json.dumps(config_data, indent=2, ensure_ascii=False)
                self.config_editor.setPlainText(formatted_json)
        except Exception as e:
            self.config_editor.setPlainText(f"加载配置文件失败：{str(e)}")
