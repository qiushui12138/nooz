import json
import logging
import os
import time
import importlib
from concurrent.futures import ThreadPoolExecutor
from typing import List
from playwright.sync_api import sync_playwright
from PyQt6.QtCore import QThread, QMutex, QMutexLocker
from infrastructure.qt_log import sing
from core.browser.ads import ADS


class WorkerThread(QThread):
    def __init__(
        self,
        selected_options: List[str],
        data: list,
        script_type,
        preview_config: dict = None,
    ):
        super().__init__()
        self.selected_options = selected_options
        self.data = data
        self.script_type = script_type
        self.mutex = QMutex()
        self._is_running = True
        self.tasks_config = self._load_tasks_config()

        # 设置默认配置
        self.preview_config = preview_config or {
            "threads": 1,
            "retry_times": 0,
            "retry_interval": 0,
        }

    def _load_tasks_config(self):
        """加载任务配置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "tasks.json"
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(e)
            sing.log_signal.emit(("ERROR", f"加载任务配置失败"))
            return {}

    def _execute_single_task(self, task_instance, options, data_item):
        """执行单个任务，包含重试逻辑"""
        ads_instance = None
        try:
            # 创建 ADS 实例并启动浏览器
            ads_instance = ADS(user_id=data_item[0])
            ws_url = ads_instance.start_remote_browser()

            if not ws_url:
                sing.log_signal.emit(("ERROR", f"启动远程浏览器失败: {data_item[0]}"))
                return False

            # 使用 playwright 连接到远程浏览器
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(ws_url)
                context = browser.contexts[0]  # 使用已存在的上下文
                page = context.pages[0]  # 使用已存在的页面

                for retry in range(self.preview_config["retry_times"] + 1):
                    try:
                        task_instance.execute_task(
                            base_page=page,
                            user_id=data_item[0],
                            evm_address=data_item[1],
                            evm_passwd=data_item[2],
                            task=options[0],
                        )
                        return True
                    except Exception as e:
                        if retry < self.preview_config["retry_times"]:
                            logging.error(e)
                            sing.log_signal.emit(
                                (
                                    "WARNING",
                                    f"任务执行失败，将在{self.preview_config['retry_interval']}秒后重试",
                                )
                            )
                            time.sleep(self.preview_config["retry_interval"])
                        else:
                            logging.error(e)
                            sing.log_signal.emit(
                                ("ERROR", f"任务执行失败，已达到最大重试次数")
                            )
                            return False
        finally:
            # 确保关闭远程浏览器
            if ads_instance:
                ads_instance.stop_remote_browser()

    def run(self):
        try:
            with QMutexLocker(self.mutex):
                if not self._is_running:
                    return

                if self.script_type not in self.tasks_config:
                    raise ValueError(f"未知的脚本类型: {self.script_type}")

                task_info = self.tasks_config[self.script_type]
                module_path = task_info.get("module")
                class_name = task_info.get("class")

                if not module_path or not class_name:
                    raise ValueError(f"任务配置不完整: {self.script_type}")

                # 动态导入任务类
                module = importlib.import_module(module_path)
                task_class = getattr(module, class_name)

                # 使用线程池执行任务
                with ThreadPoolExecutor(
                    max_workers=self.preview_config["threads"]
                ) as executor:
                    futures = []
                    for data_item in self.data:
                        if not self._is_running:
                            break
                        task_instance = task_class()
                        future = executor.submit(
                            self._execute_single_task,
                            task_instance,
                            self.selected_options,
                            data_item,
                        )
                        futures.append(future)

                    # 等待所有任务完成
                    for future in futures:
                        if not self._is_running:
                            break
                        future.result()

        except Exception as e:
            logging.error(e)
            sing.log_signal.emit(("ERROR", f"任务执行失败"))
        finally:
            if self.playwright:
                self.playwright.stop()

    def stop(self):
        with QMutexLocker(self.mutex):
            self._is_running = False
