from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDialog,
    QPlainTextEdit,
)

from config.config import custom_config


class TasksDialog(QDialog):
    def __init__(self, tasks_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("任务配置")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # 创建文本编辑器
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(tasks_content)
        self.editor.setReadOnly(True)  # 设置为只读
        self.editor.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """
        )

        layout.addWidget(self.editor)

        # 添加关闭按钮
        button_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """
        )
        close_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)


class LocalSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_config()
        self.setup_signals()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 添加任务配置按钮
        tasks_button_layout = QHBoxLayout()
        self.view_tasks_btn = QPushButton("查看任务配置")
        self.view_tasks_btn.setStyleSheet(
            """
                   QPushButton {
                       background-color: #2d2d2d;
                       border: 1px solid #3a3a3a;
                       border-radius: 4px;
                       padding: 8px 16px;
                       color: #ffffff;
                       min-width: 120px;
                   }
                   QPushButton:hover {
                       background-color: #3a3a3a;
                   }
               """
        )
        tasks_button_layout.addWidget(self.view_tasks_btn)
        tasks_button_layout.addStretch()
        main_layout.addLayout(tasks_button_layout)

        # Captcha API Keys 配置组
        captcha_group = self.create_group_box("验证码API配置")
        captcha_layout = QVBoxLayout(captcha_group)

        self.yes_captcha_input = self.create_input_row("YesCaptcha Key:")
        self.no_captcha_input = self.create_input_row("NoCaptcha Key:")
        self.two_captcha_input = self.create_input_row("2Captcha Key:")

        for widget in [
            self.yes_captcha_input,
            self.no_captcha_input,
            self.two_captcha_input,
        ]:
            captcha_layout.addLayout(widget)

        # 浏览器配置组
        browser_group = self.create_group_box("浏览器配置")
        browser_layout = QVBoxLayout(browser_group)

        self.ads_url_input = self.create_input_row("ADS Browser URL:")
        self.bit_url_input = self.create_input_row("Bit Browser URL:")

        for widget in [self.ads_url_input, self.bit_url_input]:
            browser_layout.addLayout(widget)

        # 按钮组
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """
        )
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)

        # 添加所有组件到主布局
        for widget in [captcha_group, browser_group, button_layout]:
            (
                main_layout.addWidget(widget)
                if isinstance(widget, QGroupBox)
                else main_layout.addLayout(widget)
            )
        main_layout.addStretch()

    def create_group_box(self, title):
        group = QGroupBox(title)
        group.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 12px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )
        return group

    def create_input_row(self, label_text):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setMinimumWidth(120)
        label.setStyleSheet("color: #e0e0e0;")

        input_field = QLineEdit()
        input_field.setStyleSheet(
            """
            QLineEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #264f78;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """
        )

        layout.addWidget(label)
        layout.addWidget(input_field)
        return layout

    def setup_signals(self):
        self.save_btn.clicked.connect(self.save_config)
        self.view_tasks_btn.clicked.connect(self.show_tasks_dialog)

    def show_tasks_dialog(self):
        tasks_content = custom_config.get_tasks_config()
        if tasks_content:
            dialog = TasksDialog(tasks_content, self)
            dialog.exec()
        else:
            QMessageBox.critical(self, "错误", "无法读取任务配置")

    def load_config(self):
        """从配置加载数据"""
        try:
            config_data = custom_config.get_all_config()

            # 设置输入框的值
            self.yes_captcha_input.itemAt(1).widget().setText(
                config_data["yes_captcha_key"]
            )
            self.no_captcha_input.itemAt(1).widget().setText(
                config_data["no_captcha_key"]
            )
            self.two_captcha_input.itemAt(1).widget().setText(
                config_data["2captcha_key"]
            )
            self.ads_url_input.itemAt(1).widget().setText(config_data["ads_url"])
            self.bit_url_input.itemAt(1).widget().setText(config_data["bit_url"])

        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置失败：{str(e)}")

    def save_config(self):
        """保存配置"""
        try:
            config_data = {
                "yes_captcha_key": self.yes_captcha_input.itemAt(1).widget().text(),
                "no_captcha_key": self.no_captcha_input.itemAt(1).widget().text(),
                "2captcha_key": self.two_captcha_input.itemAt(1).widget().text(),
                "ads_url": self.ads_url_input.itemAt(1).widget().text(),
                "bit_url": self.bit_url_input.itemAt(1).widget().text(),
            }

            custom_config.save_config(config_data)
            QMessageBox.information(self, "成功", "配置已保存")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败：{str(e)}")
