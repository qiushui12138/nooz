import json
import os
from typing import Dict, List


class TaskManager:
    def __init__(self):
        self.tasks_config = {}
        self.load_tasks()

    def load_tasks(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "tasks.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            self.tasks_config = json.load(f)

    def get_script_tasks(self, script_name: str) -> List[Dict]:
        return self.tasks_config.get(script_name, {}).get("tasks", [])

    def get_all_scripts(self) -> List[str]:
        return list(self.tasks_config.keys())


task_manager = TaskManager()
