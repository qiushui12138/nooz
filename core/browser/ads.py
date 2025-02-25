import logging

import requests

from config.config import custom_config
from infrastructure import ter_log

"""
    Author : RoyHe
    Mail   : habaihua666@gmail.com
    Date   : 11:51 2025/2/13
    Description : AdsPower LocalApi 
"""

ter_log.setup_logging()


class ADS:
    def __init__(self, user_id, open_tabs=0, headless=0):

        self.url = custom_config.get_ads()

        self.user_id = user_id

        # 0 有头 1 无头
        self.headless = headless
        # 历史页面
        self.open_tabs = open_tabs

    def start_remote_browser(self):
        """启动远程浏览器"""
        try:
            response = requests.get(
                f"{self.url}/browser/start?user_id={self.user_id}&open_tabs={self.open_tabs}&headless={self.headless}"
            )
            response.raise_for_status()
            data = response.json()

            print(data)
            if data["code"] != 0:
                raise ValueError("远程浏览器启动失败")
            return data["data"]["ws"]["puppeteer"]
        except Exception:
            return None

    def stop_remote_browser(self):
        """停止远程浏览器"""
        try:
            requests.get(f"{self.url}/browser/stop?user_id={self.user_id}")
        except requests.RequestException:
            logging.error(f"关闭浏览器失败: {self.user_id}")

    def update_remote_browser(self):
        """更新环境信息"""
        try:
            body = {
                "user_id": self.user_id,
                "open_urls": [
                    "https://www.x.com/home",
                    "https://discord.com/channels/@me",
                    "https://gmail.com",
                ],
            }

            logging.info(f"访问地址为: {self.url}/user/update")
            response = requests.post(f"{self.url}/user/update", json=body)
            response.raise_for_status()
            data = response.json()
            logging.info(f"更新浏览器数据成功:{data}")  # 记录API返回

            if data["code"] != 0:
                raise ValueError("远程浏览器更新数据失败")
        except requests.RequestException as e:
            logging.error(f"网络请求错误: {e}")

        except ValueError as e:
            logging.error(e)
