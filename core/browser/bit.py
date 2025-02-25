import logging

import requests

from config.config import custom_config
from infrastructure import ter_log

"""
    Author : RoyHe
    Mail   : habaihua666@gmail.com
    Date   : 11:51 2025/2/25
    Description : Bit LocalApi 
"""


class Bit:
    def __init__(self, bit_id, open_tabs=0, headless=0):
        self.url = custom_config.get_bit()

        self.bit_id = bit_id

        # 0 有头 1 无头
        self.headless = headless
        # 历史页面
        self.open_tabs = open_tabs

    def start_remote_browser(self):
        """启动远程浏览器"""
        try:
            response = requests.get(f"{self.url}/browser/open?id={self.bit_id}")
            response.raise_for_status()
            data = response.json()
            if data["code"] != 0:
                raise ValueError("远程浏览器启动失败")
            return data["data"]["ws"]["puppeteer"]
        except Exception:
            return None
