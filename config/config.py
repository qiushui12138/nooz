import configparser
import json
import os
from typing import Dict, Optional


class Config:
    def __init__(self, config_file="config.ini"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, config_file)
        self.tasks_path = os.path.join(self.base_dir, "tasks.json")

        # 初始化配置解析器
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        if not os.path.isfile(self.config_path):
            raise RuntimeError(f"配置文件不存在于: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config.read_file(f)
        except UnicodeDecodeError:
            with open(self.config_path, "r", encoding="gbk") as f:
                self.config.read_file(f)

    def get_yes_captcha_key(self) -> str:
        return self.config.get("yes_captcha", "key", fallback="")

    def get_no_captcha_key(self) -> str:
        return self.config.get("no_captcha", "key", fallback="")

    def get_2captcha_key(self) -> str:
        return self.config.get("2captcha", "key", fallback="")

    def get_ads(self) -> str:
        return self.config.get("ads", "url", fallback="")

    def get_bit(self) -> str:
        return self.config.get("bit", "url", fallback="")

    def get_all_config(self) -> Dict[str, str]:
        """获取所有配置"""
        return {
            "yes_captcha_key": self.get_yes_captcha_key(),
            "no_captcha_key": self.get_no_captcha_key(),
            "2captcha_key": self.get_2captcha_key(),
            "ads_url": self.get_ads(),
            "bit_url": self.get_bit(),
        }

    def save_config(self, config_data: Dict[str, str]) -> None:
        """保存配置"""
        # 确保所有节点存在
        for section in ["yes_captcha", "no_captcha", "2captcha", "ads", "bit"]:
            if not self.config.has_section(section):
                self.config.add_section(section)

        # 更新配置
        self.config.set("yes_captcha", "key", config_data.get("yes_captcha_key", ""))
        self.config.set("no_captcha", "key", config_data.get("no_captcha_key", ""))
        self.config.set("2captcha", "key", config_data.get("2captcha_key", ""))
        self.config.set("ads", "url", config_data.get("ads_url", ""))
        self.config.set("bit", "url", config_data.get("bit_url", ""))

        # 写入文件
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    def get_tasks_config(self) -> Optional[str]:
        """读取任务配置"""
        try:
            with open(self.tasks_path, "r", encoding="utf-8") as f:
                return json.dumps(json.load(f), indent=2, ensure_ascii=False)
        except Exception:
            return None


custom_config = Config()
