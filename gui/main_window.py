import os
import re
import time
from typing import Set

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QSplitter,
    QScrollArea,
    QGridLayout,
    QMessageBox,
    QFileDialog,
    QDockWidget,
    QWidget,
    QApplication,
)

from core.work_thread import WorkerThread
from gui.components.control_group import ControlGroup
from gui.components.file_group import FileGroup
from gui.components.log_group import LogGroup
from gui.components.preview_group import PreviewGroup
from gui.components.sidebar import Sidebar
from gui.styles.modern_style import ModernStyle
from gui.tools.balance_checker import BalanceChecker
from infrastructure.qt_log import sing


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.excel_data = []

        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 创建组件
        self.create_components()

        # 创建菜单
        self.create_menus()

        # 初始化界面
        self.init_ui()
        self.setup_signals()

    def create_components(self):
        """创建所有组件"""
        # 创建主要组件
        self.sidebar = Sidebar()
        self.file_group = FileGroup()
        self.control_group = ControlGroup()
        self.preview_group = PreviewGroup()
        self.log_group = LogGroup(self)

        # 创建工作区容器
        self.work_content = QWidget()
        self.work_layout = QGridLayout(self.work_content)
        self.work_layout.setSpacing(15)

        # 添加脚本相关组件到工作区
        self.work_layout.addWidget(self.file_group, 0, 0)
        self.work_layout.addWidget(self.control_group, 1, 0)
        self.work_layout.addWidget(self.preview_group, 2, 0)

        # 创建日志停靠窗口
        self.log_dock = QDockWidget("日志", self)
        self.log_dock.setWidget(self.log_group)
        self.log_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

    def create_menus(self):
        """创建菜单栏"""
        view_menu = self.menuBar().addMenu("视图")
        self.toggle_log_action = QAction("显示/隐藏日志", self)
        self.toggle_log_action.setCheckable(True)
        self.toggle_log_action.setChecked(True)
        self.toggle_log_action.triggered.connect(self.toggle_log_dock)
        view_menu.addAction(self.toggle_log_action)

        # 添加帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(check_update_action)

        # 连接日志窗口可见性变化信号
        self.log_dock.visibilityChanged.connect(self.on_log_dock_visibility_changed)

    def check_for_updates(self):
        """检查更新"""
        from gui.dialogs.update_dialog import UpdateDialog

        dialog = UpdateDialog(self)
        dialog.exec()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和图标
        self.setWindowTitle("Nooz")
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "static", "iconfull.ico"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 设置窗口大小和位置
        screen = QApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        self.setGeometry(
            (screen.width() - window_width) // 2,
            (screen.height() - window_height) // 2,
            window_width,
            window_height,
        )

        # 创建主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 添加侧边栏
        main_splitter.addWidget(self.sidebar)

        # 创建工作区
        work_area = QScrollArea()
        work_area.setWidgetResizable(True)
        work_area.setWidget(self.work_content)
        main_splitter.addWidget(work_area)

        # 添加到主布局
        self.main_layout.addWidget(main_splitter)

        # 添加日志窗口
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)

        # 设置初始大小
        main_splitter.setSizes([200, 700])

        # 应用样式
        self.apply_modern_style()

    def apply_modern_style(self):
        """应用现代化样式"""
        self.setStyleSheet(ModernStyle.get_style())

    def on_script_changed(self, script_name):
        """切换脚本时的处理"""
        self.control_group.switch_script_options(script_name)
        self.show_info(f"已切换到脚本：{script_name}")

    def handle_log(self, log_tuple):
        """处理来自工作线程的日志信号"""
        level, message = log_tuple
        self.log_group.add_log_entry(time.time(), level, message)

    def start_task(self):
        """开始任务"""
        if not self.excel_data:
            self.show_warning("请先导入数据文件！")
            return

        selected_rows = self.control_group.get_selected_rows()
        if not selected_rows:
            self.show_warning("请选择要执行的行！")
            return

        task_data = self.prepare_task_data(selected_rows)
        if not task_data:
            self.show_warning("选择的行号超出范围！")
            return

        tasks = self.control_group.get_selected_tasks()
        if not tasks:
            self.show_warning("请选择要执行的任务！")
            return

        self.start_worker_thread(tasks, task_data)

    def on_log_dock_visibility_changed(self, visible):
        """处理日志窗口可见性变化"""
        self.toggle_log_action.setChecked(visible)

    def setup_signals(self):
        """设置信号连接"""
        # 文件操作信号
        self.file_group.excel_loaded.connect(self.on_excel_loaded)

        # 任务控制信号
        self.control_group.start_btn.clicked.connect(self.start_task)
        self.control_group.stop_btn.clicked.connect(self.stop_task)

        # 日志相关信号
        self.log_group.export_btn.clicked.connect(self.export_log)
        sing.log_signal.connect(self.handle_log)

        # 侧边栏信号
        sing.menu_selected.connect(self.on_menu_selected)

    def on_excel_loaded(self, data, total_rows):
        """处理Excel加载完成事件"""
        self.excel_data = data
        self.control_group.set_row_input(f"1-{total_rows}")

    def on_menu_selected(self, primary_text, secondary_text):
        """处理菜单选择事件"""
        if primary_text == "脚本启动器":
            self.show_script_page(secondary_text)
        elif primary_text == "工具":
            self.show_tools_page(secondary_text)
        elif primary_text == "设置":
            self.show_settings_page(secondary_text)

    def show_script_page(self, script_name):
        """显示脚本页面"""
        # 隐藏其他页面组件
        for i in reversed(range(self.work_layout.count())):
            self.work_layout.itemAt(i).widget().setVisible(False)

        # 显示脚本相关组件
        self.file_group.setVisible(True)
        self.control_group.setVisible(True)
        self.preview_group.setVisible(True)
        self.control_group.switch_script_options(script_name)

    def show_tools_page(self, tool_name):
        """显示工具页面"""
        # 隐藏脚本相关组件
        self.file_group.setVisible(False)
        self.control_group.setVisible(False)
        self.preview_group.setVisible(False)

        # 隐藏所有工具和设置组件
        if hasattr(self, "balance_checker"):
            self.balance_checker.setVisible(False)
        if hasattr(self, "gas_monitor"):
            self.gas_monitor.setVisible(False)
        if hasattr(self, "proxy_settings"):
            self.proxy_settings.setVisible(False)
        if hasattr(self, "local_settings"):
            self.local_settings.setVisible(False)

        if tool_name == "余额查询":
            if not hasattr(self, "balance_checker"):
                self.balance_checker = BalanceChecker()
                self.work_layout.addWidget(self.balance_checker, 0, 0)
            self.balance_checker.setVisible(True)
        elif tool_name == "Gas监控":
            from gui.tools.gas_monitor import GasMonitor

            if not hasattr(self, "gas_monitor"):
                self.gas_monitor = GasMonitor()
                self.work_layout.addWidget(self.gas_monitor, 0, 0)
            self.gas_monitor.setVisible(True)
        else:
            self.show_info(f"工具页面：{tool_name} - 开发中")

    def show_settings_page(self, setting_name):
        """显示设置页面"""
        # 清除工作区现有内容
        for i in reversed(range(self.work_layout.count())):
            self.work_layout.itemAt(i).widget().setVisible(False)

        if setting_name == "代理设置":
            from gui.settings.proxy_settings import ProxySettings

            if not hasattr(self, "proxy_settings"):
                self.proxy_settings = ProxySettings()
                self.work_layout.addWidget(self.proxy_settings, 0, 0)
            self.proxy_settings.setVisible(True)
        elif setting_name == "本地设置":
            from gui.settings.local_settings import LocalSettings

            if not hasattr(self, "local_settings"):
                self.local_settings = LocalSettings()
                self.work_layout.addWidget(self.local_settings, 0, 0)
            self.local_settings.setVisible(True)
        else:
            self.show_info(f"设置页面：{setting_name} - 开发中")

    def toggle_log_dock(self, checked):
        """切换日志窗口显示状态"""
        if checked:
            self.log_dock.show()
        else:
            self.log_dock.hide()

    def start_worker_thread(self, tasks, task_data):
        """启动工作线程以执行任务"""
        script_type = self.sidebar.currentScript()
        if not script_type:
            self.show_warning("请选择一个脚本！")
            return

        try:
            # 获取预览配置
            preview_config = self.preview_group.get_config()

            self.worker_thread = WorkerThread(
                selected_options=tasks,
                data=task_data,
                script_type=script_type,
                preview_config=preview_config,  # 传入预览配置
            )
            self.worker_thread.finished.connect(self.on_task_finished)
            self.worker_thread.started.connect(self.on_task_started)
            self.worker_thread.start()
        except Exception as e:
            self.show_error(f"启动任务失败: {str(e)}")

    def prepare_task_data(self, selected_rows):
        """
        准备任务数据。

        Args:
            selected_rows: 选中的行号列表（从1开始）。

        Returns:
            list: 选中的数据行。
        """
        task_data = []
        for row in selected_rows:
            idx = row - 1  # 行号从1开始，转换为0-based索引
            if 0 <= idx < len(self.excel_data):
                task_data.append(self.excel_data[idx])
            else:
                self.show_warning(f"行号 {row} 超出范围")
        return task_data

    def stop_task(self):
        """停止任务"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()

    def on_task_started(self):
        """任务开始时的UI更新"""

        self.file_group.disable_controls()

    def on_task_finished(self):
        """任务结束时的UI更新"""
        self.worker_thread = None

        self.file_group.enable_controls()
        self.show_info("任务已完成")

    def show_error(self, message: str):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)

    def show_warning(self, message: str):
        """显示警告消息"""
        QMessageBox.warning(self, "警告", message)

    def show_info(self, message: str):
        """显示信息消息"""
        QMessageBox.information(self, "提示", message)

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "任务运行中",
                "确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_task()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def validate_selection(self, selection: str) -> Set[int]:
        """验证行选择输入"""
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
        max_row = len(self.excel_data)
        invalid = [x for x in selected if x < 1 or x > max_row]
        if invalid:
            raise ValueError(f"无效行号: {invalid}, 有效范围1-{max_row}")
        return selected

    def export_log(self):
        """导出日志到Excel"""
        if self.log_group.log_table.rowCount() == 0:
            self.show_warning("没有可导出的日志")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "", "Excel 文件 (*.xlsx)"
        )
        if file_path:
            try:
                data = []
                for row in range(self.log_group.log_table.rowCount()):
                    row_data = []
                    for col in range(self.log_group.log_table.columnCount()):
                        item = self.log_group.log_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                df = pd.DataFrame(data, columns=["时间", "级别", "内容"])
                df.to_excel(file_path, index=False)
                self.show_info("日志导出成功")
            except Exception as e:
                self.show_error(f"日志导出失败: {str(e)}")
