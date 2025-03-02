import logging
from typing import List

from playwright.sync_api import Page, sync_playwright

from core.browser import ads
from infrastructure.qt_log import sing


class BaseTask:
    def execute_task(
        self,
        base_page: Page,
        user_id: str,
        evm_address: str,
        evm_passwd: str,
        task: str,
    ) -> None:
        """执行具体任务的抽象方法"""
        raise NotImplementedError

    def main(self, tasks: List[str], data: List[str]) -> None:
        """通用的主函数实现"""
        for user_id, evm_address, evm_passwd in data:
            sing.log_signal.emit(("INFO", f"处理用户: {user_id}"))

            try:
                ads_browser = ads.ADS(user_id)
                ws_endpoint = ads_browser.start_remote_browser()

                if not ws_endpoint:
                    logging.error(f"无法启动浏览器，跳过 {user_id}")
                    continue

                with sync_playwright() as p:
                    browser = p.chromium.connect_over_cdp(ws_endpoint)
                    if not browser:
                        logging.error("无法连接到远程浏览器")
                        continue

                    context = browser.contexts[0] if browser.contexts else None
                    if not context:
                        logging.error("没有可用的浏览器上下文")
                        continue

                    base_page = context.pages[0] if context.pages else None
                    if not base_page:
                        logging.error("没有可用的页面")
                        continue

                    base_page.bring_to_front()

                    # 执行每个任务
                    for task in tasks:
                        self.execute_task(
                            base_page, user_id, evm_address, evm_passwd, task
                        )

            except Exception as e:
                logging.error(f"处理用户 {user_id} 时发生异常: {str(e)}")
            finally:
                if "browser" in locals():
                    try:
                        ads_browser.stop_remote_browser()
                    except Exception as e:
                        logging.error(f"关闭浏览器时出错: {e}")
