import json
import os
import importlib
from typing import List
from PyQt6.QtCore import QThread, QMutex, QMutexLocker
from infrastructure.qt_log import sing


class WorkerThread(QThread):
    def __init__(self, selected_options: List[str], data: list, script_type):
        super().__init__()
        self.selected_options = selected_options
        self.data = data
        self.script_type = script_type
        self.mutex = QMutex()
        self._is_running = True
        self.tasks_config = self._load_tasks_config()

    def _load_tasks_config(self):
        """加载任务配置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "tasks.json"
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            sing.log_signal.emit(("ERROR", f"加载任务配置失败: {str(e)}"))
            return {}

    def run(self):
        try:
            with QMutexLocker(self.mutex):
                if not self._is_running:
                    return

                if self.script_type not in self.tasks_config:
                    raise ValueError(f"未知的脚本类型: {self.script_type}")

                # 从配置中获取任务信息
                task_info = self.tasks_config[self.script_type]
                module_path = task_info.get("module")
                class_name = task_info.get("class")

                if not module_path or not class_name:
                    raise ValueError(f"任务配置不完整: {self.script_type}")

                # 动态导入模块和类
                try:
                    module = importlib.import_module(module_path)
                    task_class = getattr(module, class_name)
                except ImportError as e:
                    raise ImportError(f"导入模块失败 {module_path}: {str(e)}")
                except AttributeError as e:
                    raise AttributeError(f"类不存在 {class_name}: {str(e)}")

                # 实例化并执行任务
                task_instance = task_class()
                task_instance.main(self.selected_options, self.data)

        except Exception as e:
            sing.log_signal.emit(("ERROR", f"任务执行失败: {str(e)}"))

    def stop(self):
        with QMutexLocker(self.mutex):
            self._is_running = False
