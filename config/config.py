"""
    Author : RoyHe
    Mail   : habaihua666@gmail.com
    Date   : 11:51 2025/2/13
    Description : Config.ini Read
"""

import configparser
import os


class Config:
    def __init__(self, config_file="config.ini"):
        # 动态获取当前脚本所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, config_file)

        # 验证文件存在性
        if not os.path.isfile(self.config_path):
            raise RuntimeError(f"配置文件不存在于: {self.config_path}")

        # 初始化配置解析器
        self.config = configparser.ConfigParser()

        # 处理编码问题
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config.read_file(f)
        except UnicodeDecodeError:
            with open(self.config_path, "r", encoding="gbk") as f:
                self.config.read_file(f)

    def get_yes_captcha_key(self):
        return self.config.get("yes_captcha", "key")

    def get_ads(self):
        return self.config.get("ads", "url")

    def get_bit(self):
        return self.config.get("bit", "url")


custom_config = Config()
