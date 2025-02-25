from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QWidget,
)


class PreviewGroup(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("运行配置", parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 线程数配置
        thread_row = QWidget()
        thread_layout = QHBoxLayout(thread_row)
        thread_layout.addWidget(QLabel("线程数："))
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 10)
        self.thread_spin.setValue(3)
        thread_layout.addWidget(self.thread_spin)
        thread_layout.addStretch()
        layout.addWidget(thread_row)

        # 重试次数配置
        retry_row = QWidget()
        retry_layout = QHBoxLayout(retry_row)
        retry_layout.addWidget(QLabel("重试次数："))
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 5)
        self.retry_spin.setValue(3)
        retry_layout.addWidget(self.retry_spin)
        retry_layout.addStretch()
        layout.addWidget(retry_row)

        # 重试间隔配置
        interval_row = QWidget()
        interval_layout = QHBoxLayout(interval_row)
        interval_layout.addWidget(QLabel("重试间隔(秒)："))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 300)
        self.interval_spin.setValue(60)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        layout.addWidget(interval_row)

        layout.addStretch()
        self.setLayout(layout)

    def get_config(self) -> dict:
        """获取当前配置"""
        return {
            "threads": self.thread_spin.value(),
            "retry_times": self.retry_spin.value(),
            "retry_interval": self.interval_spin.value(),
        }

    def set_config(self, config: dict):
        """设置配置"""
        if "threads" in config:
            self.thread_spin.setValue(config["threads"])
        if "retry_times" in config:
            self.retry_spin.setValue(config["retry_times"])
        if "retry_interval" in config:
            self.interval_spin.setValue(config["retry_interval"])
