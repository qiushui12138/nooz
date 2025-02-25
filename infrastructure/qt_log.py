from PyQt6.QtCore import QObject, pyqtSignal


class GlobalSignals(QObject):
    log_signal = pyqtSignal(tuple)
    menu_selected = pyqtSignal(str, str)  # 发送一级菜单和二级菜单的选择


sing = GlobalSignals()
