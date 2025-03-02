from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
)

from config.task_manager import task_manager
from infrastructure.qt_log import sing


class Sidebar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 一级菜单
        self.primary_menu = QListWidget()
        self.primary_menu.setFixedWidth(150)
        self.primary_menu.addItems(["脚本启动器", "工具", "设置"])
        self.primary_menu.setStyleSheet(
            """
            QListWidget {
                border: none;
                background-color: #1e1e1e;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 0px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #2d2d2d;
            }
        """
        )

        # 二级菜单容器
        self.secondary_menu_stack = QStackedWidget()
        self.secondary_menu_stack.setFixedWidth(150)
        self.secondary_menu_stack.setStyleSheet(
            """
            QListWidget {
                border: none;
                background-color: #252525;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 0px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #2d2d2d;
            }
        """
        )

        # 创建二级菜单
        self.setup_secondary_menus()

        # 将脚本列表设为可访问属性
        self.script_list = self.secondary_menu_stack.widget(0)  # 脚本启动器菜单

        layout.addWidget(self.primary_menu)
        layout.addWidget(self.secondary_menu_stack)

    def setup_secondary_menus(self):
        # 脚本启动器二级菜单
        scripts_menu = QListWidget()
        scripts_menu.addItems(task_manager.get_all_scripts())
        self.secondary_menu_stack.addWidget(scripts_menu)

        # 工具二级菜单
        tools_menu = QListWidget()
        tools_menu.addItems(["余额查询", "Gas监控"])
        self.secondary_menu_stack.addWidget(tools_menu)

        # 设置二级菜单
        settings_menu = QListWidget()
        settings_menu.addItems(["代理设置", "本地设置"])
        self.secondary_menu_stack.addWidget(settings_menu)

    def setup_signals(self):
        self.primary_menu.currentRowChanged.connect(
            self.secondary_menu_stack.setCurrentIndex
        )
        self.primary_menu.currentRowChanged.connect(self.on_primary_menu_changed)

        # 连接所有二级菜单的信号
        for i in range(self.secondary_menu_stack.count()):
            menu = self.secondary_menu_stack.widget(i)
            if isinstance(menu, QListWidget):
                menu.itemClicked.connect(self.on_secondary_menu_clicked)

        # 默认选中第一项
        self.primary_menu.setCurrentRow(0)

    def on_primary_menu_changed(self, index):
        primary_text = self.primary_menu.item(index).text()
        secondary_menu = self.secondary_menu_stack.widget(index)
        if secondary_menu.count() > 0:
            secondary_menu.setCurrentRow(0)
            sing.menu_selected.emit(primary_text, secondary_menu.item(0).text())

    def on_secondary_menu_clicked(self, item):
        primary_text = self.primary_menu.currentItem().text()
        secondary_text = item.text()
        # 直接发送菜单选择信号
        sing.menu_selected.emit(primary_text, secondary_text)

    def currentScript(self):
        """获取当前选中的脚本名称"""
        if self.primary_menu.currentRow() == 0:  # 确保是在脚本启动器页面
            return (
                self.script_list.currentItem().text()
                if self.script_list.currentItem()
                else None
            )
        return None
