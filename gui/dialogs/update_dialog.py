import os
import subprocess
import sys

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
)


class UpdateWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_cancelled = False

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get("content-length", 0))

            if total_size == 0:
                self.finished.emit(False, "无法获取更新文件大小")
                return

            block_size = 1024
            downloaded = 0

            with open(self.save_path, "wb") as f:
                for data in response.iter_content(block_size):
                    if self._is_cancelled:
                        return
                    downloaded += len(data)
                    f.write(data)
                    progress = int((downloaded / total_size) * 100)
                    self.progress.emit(progress)

            self.finished.emit(True, "更新下载完成")
        except Exception as e:
            self.finished.emit(False, f"更新失败: {str(e)}")

    def cancel(self):
        self._is_cancelled = True


class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("软件更新")
        self.setMinimumWidth(400)
        self.worker = None
        self.setup_ui()
        self.check_for_updates()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.status_label = QLabel("正在检查更新...", self)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()

        self.update_button = QPushButton("立即更新", self)
        self.update_button.setVisible(False)
        self.update_button.clicked.connect(self.start_update)
        button_layout.addWidget(self.update_button)

        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def check_for_updates(self):
        try:
            # 从服务器获取版本信息
            response = requests.get("http://121.41.97.25/")
            version_info = response.json()

            current_version = "1.0.0"  # 从配置文件获取当前版本
            latest_version = version_info["version"]

            if latest_version > current_version:
                self.status_label.setText(f"发现新版本: {latest_version}")
                self.update_button.setVisible(True)
            else:
                self.status_label.setText("当前已是最新版本")
        except Exception as e:
            self.status_label.setText(f"检查更新失败: {str(e)}")

    def start_update(self):
        self.update_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 开始下载更新
        save_path = os.path.join(os.getenv("TEMP"), "update.exe")
        self.worker = UpdateWorker("https://example.com/update.exe", save_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.handle_update_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_update_finished(self, success, message):
        if success:
            reply = QMessageBox.question(
                self,
                "更新完成",
                "更新已下载完成，是否立即安装？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.install_update()
        else:
            QMessageBox.critical(self, "错误", message)
            self.update_button.setEnabled(True)

    def install_update(self):
        save_path = os.path.join(os.getenv("TEMP"), "update.exe")
        subprocess.Popen([save_path])
        sys.exit(0)

    def reject(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        super().reject()
