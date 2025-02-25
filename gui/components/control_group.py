from typing import List, Set
from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QCheckBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
import re

from config.task_manager import TaskManager


class ControlGroup(QGroupBox):
    taskStarted = pyqtSignal()
    taskStopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("任务控制", parent)
        self.task_manager = TaskManager()
        self.checkboxes = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 行选择器
        self.setup_row_selector(layout)

        # 任务选项
        self.setup_task_options(layout)

        # 按钮区域
        self.setup_control_buttons(layout)

        self.setLayout(layout)

    def setup_row_selector(self, parent_layout):
        row_selector = QWidget()
        row_layout = QHBoxLayout(row_selector)

        row_layout.addWidget(QLabel("选择执行行："))
        self.row_input = QLineEdit()
        self.row_input.setPlaceholderText("例如：1-5,8,10-12")
        row_layout.addWidget(self.row_input)

        self.quick_select_btn = QPushButton("全选")
        row_layout.addWidget(self.quick_select_btn)

        parent_layout.addWidget(row_selector)
        parent_layout.addWidget(self.create_horizontal_line())

    def setup_task_options(self, parent_layout):
        self.task_options_container = QWidget()
        self.task_options_layout = QGridLayout(self.task_options_container)

        # 动态创建任务选项
        scripts = self.task_manager.get_all_scripts()
        for i, script_name in enumerate(scripts):
            options_widget = QWidget()
            options_layout = QGridLayout(options_widget)

            tasks = self.task_manager.get_script_tasks(script_name)
            for j, task in enumerate(tasks):
                checkbox = self.create_checkbox(task["name"])
                self.checkboxes[task["id"]] = checkbox
                options_layout.addWidget(checkbox, j // 2, j % 2)

            widget_name = f"{script_name.lower().replace(' ', '_')}_options"
            setattr(self, widget_name, options_widget)
            self.task_options_layout.addWidget(options_widget)

            # 只显示第一个脚本的选项
            options_widget.setVisible(i == 0)

        parent_layout.addWidget(self.task_options_container)
        parent_layout.addWidget(self.create_horizontal_line())

    def setup_control_buttons(self, parent_layout):
        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)

        self.start_btn = self.create_button("开始任务", "start")
        self.stop_btn = self.create_button("停止任务", "stop")
        self.stop_btn.setEnabled(False)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)

        parent_layout.addWidget(button_row)

    def create_checkbox(self, text: str) -> QCheckBox:
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet(
            """
            QCheckBox {
                padding: 5px;
                border-radius: 4px;
            }
            QCheckBox:hover {
                background-color: #3a3a3a;
            }
        """
        )
        return checkbox

    def create_button(self, text: str, button_type: str) -> QPushButton:
        button = QPushButton(text)
        if button_type == "start":
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #27ae60;
                    border-radius: 5px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """
            )
        elif button_type == "stop":
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #c0392b;
                    border-radius: 5px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #e74c3c;
                }
            """
            )
        return button

    def create_horizontal_line(self):
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #404040;")
        return line

    def switch_script_options(self, script_name: str):
        # 隐藏所有选项组
        for widget in self.task_options_container.findChildren(
            QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
        ):
            widget.hide()

        # 显示选中脚本的选项组
        target_widget = getattr(
            self, f"{script_name.lower().replace(' ', '_')}_options", None
        )
        if target_widget:
            target_widget.show()

    def get_selected_tasks(self) -> List[str]:
        tasks = []
        for task_id, checkbox in self.checkboxes.items():
            if checkbox.isVisible() and checkbox.isChecked():
                tasks.append(task_id)
        return tasks

    def get_row_input(self) -> str:
        return self.row_input.text()

    def set_row_input(self, text: str):
        self.row_input.setText(text)

    def get_selected_rows(self) -> List[int]:
        """Get selected rows from input"""
        try:
            return sorted(self.validate_selection(self.row_input.text()))
        except ValueError as e:
            # Signal the error to main window
            return []

    def validate_selection(self, selection: str) -> Set[int]:
        """Validate row selection input"""
        if not selection:
            raise ValueError("请输入要执行的行")

        if not re.match(r"^\d+(-\d+)?(,\d+(-\d+)?)*$", selection):
            raise ValueError("输入格式无效")

        selected = set()
        for part in selection.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                if start > end:
                    raise ValueError("起始行不能大于结束行")
                selected.update(range(start, end + 1))
            else:
                selected.add(int(part))

        return selected
