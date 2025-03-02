import time

import requests
from playwright.sync_api import Page

from config.proxy_manager import proxy_manager
from core.tasks.base_task import BaseTask
from infrastructure.qt_log import sing
from utils.yes_captcha import YesCaptcha


class F0G(BaseTask):
    def faucet(self, base_page, evm_address, user_id):
        base_page.goto("https://faucet.0g.ai/")
        base_page.fill("#address", evm_address)
        time.sleep(3)

        with base_page.expect_request("**/getcaptcha/**") as request_info:
            iframe = base_page.query_selector('iframe[src*="hcaptcha"]')
            iframe_element = iframe.content_frame()
            checkbox = iframe_element.query_selector(
                '[role="checkbox"][aria-checked="false"]'
            )
            checkbox.click()
            request = request_info.value

        site_key = request.url.rsplit("/", 1)[-1]
        print(f"获取到 hCaptcha sitekey: {site_key}")

        yes = YesCaptcha()
        yescaptcha = yes.solve_hcaptcha_with_yescaptcha(
            base_page.url, site_key, base_page.evaluate("() => navigator.userAgent")
        )

        headers = {
            "accept": "*/*",
            "accept-language": "zh,zh-CN;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://faucet.0g.ai",
            "priority": "u=1, i",
            "referer": "https://faucet.0g.ai/",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/131.0.0.0",
        }

        # 从 proxy_manager 获取代理配置
        proxy_results = proxy_manager.search_proxies(ads_id=user_id)
        if not proxy_results:
            sing.log_signal.emit(("WARNING", f"未找到用户 {user_id} 的代理配置"))
            return

        proxy = proxy_results[0]  # 获取第一个匹配的代理
        proxy_url = f"socks5://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        print(proxy_url)
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        data = '{"address":"' + evm_address + '","hcaptchaToken":"' + yescaptcha + '"}'
        try:
            response = requests.post(
                "https://faucet.0g.ai/api/faucet",
                headers=headers,
                data=data,
                proxies=proxies,
                timeout=10,
            )
            print(evm_address, response.text)
            sing.log_signal.emit(("INFO", f"请求结果: {response.text}"))
        except Exception as e:
            sing.log_signal.emit(("ERROR", f"请求失败: {str(e)}"))

    def execute_task(
        self,
        base_page: Page,
        user_id: str,
        evm_address: str,
        evm_passwd: str,
        task: str,
    ) -> None:
        if task == "faucet":
            self.faucet(base_page, evm_address, user_id)
