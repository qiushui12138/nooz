import logging
import random
import time

from playwright.sync_api import Page

from config.config import custom_config
from core.tasks.base_task import BaseTask
from infrastructure import ter_log
from infrastructure.qt_log import sing

"""
    Author : RoyHe
    Mail   : habaihua666@gmail.com
    Date   : 11:51 2025/2/13
    Description : Main Sahara Legends
"""

ter_log.setup_logging()


class Legends(BaseTask):
    def __init__(self):
        self.config = custom_config

    def in_legends(self, base_page, click_img):
        """进入 Legends"""
        base_page.goto("https://legends.saharalabs.ai/")
        base_page.wait_for_load_state()
        time.sleep(3)

        button = base_page.get_by_text("Sign In")
        if button.count() == 1:
            button.click()
            with base_page.context.expect_page() as new_page_info:
                base_page.get_by_text("Meta").click()
            meta_page = new_page_info.value
            meta_page.click("button:has-text('確認')")
            base_page.bring_to_front()
        elif button.count() == 2:
            with base_page.context.expect_page() as new_page_info:
                base_page.get_by_text("Meta").click()
            meta_page = new_page_info.value
            meta_page.click("button:has-text('確認')")
            base_page.bring_to_front()

        old_amount_value = base_page.locator("div.amount").text_content()

        if click_img:
            img = base_page.locator('img[src*="/assets/all-normal-BQuqrsj0.png"]')
            if img.count() > 0:
                img.wait_for()
                img.click()
            img = base_page.locator('img[src*="/assets/all-claim-D56aap8V.png"]')
            if img.count() > 0:
                img.wait_for()
                img.click()
        time.sleep(5)

        return old_amount_value, base_page

    def legends(self, evm_passwd, base_page):

        try:
            base_page.goto(
                "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"
            )
            base_page.wait_for_load_state()
            time.sleep(3)

            flag = True
            out = 0
            while flag:
                try:
                    base_page.locator("#password").fill(evm_passwd)
                    base_page.click("button:has-text('解鎖')")
                    time.sleep(3)
                    flag = False
                except Exception:
                    base_page.reload()
                    base_page.wait_for_load_state()
                    out += 1
                    if out > 3:
                        raise ValueError("Galaxy Blog Error")

            old_amount_value, base_page = self.in_legends(base_page, click_img=True)
            logging.info(f"当前页面: {base_page.url}")

            with base_page.context.expect_page() as new_page_info:
                base_page.get_by_text("Sahara AI Blog").click()
            galxe_page = new_page_info.value
            galxe_page.wait_for_load_state()

            logging.info(f"新页面已打开: {galxe_page.url}")
            time.sleep(3)

            blog = galxe_page.get_by_text("Daily Visit the Sahara AI Blog")

            flag = True
            out = 0
            while flag:
                try:
                    logging.info("尝试点击")
                    galxe_page.get_by_text("Daily Visit the Sahara AI Blog").click()
                    time.sleep(3)
                    flag = False
                except Exception:
                    galxe_page.reload()
                    galxe_page.wait_for_load_state()
                    out += 1
                    if out > 3:
                        raise ValueError("Galaxy Blog Error")

            logging.info(f"当前页面: {galxe_page.url}")

            button = galxe_page.get_by_text("Meta")
            if button.count() > 0:
                logging.info("获取到Meta连线")
                with galxe_page.context.expect_page() as new_page_info:
                    button.click()
                meta2_page = new_page_info.value

                logging.info(f"MetaMask 页面已打开: {meta2_page.url}")

                meta2_page.click("button:has-text('連線')")

                time.sleep(5)

                logging.info(f"当前页面: {meta2_page.url}")

                galxe_page.bring_to_front()

                blog.click()

            try:
                galxe_page.get_by_text("Access")
            except Exception as e:
                logging.info("没有获取到Access 跳过任务")
                return galxe_page

            with galxe_page.context.expect_page() as new_page_info:
                galxe_page.get_by_text("Access").click()
            blog_page = new_page_info.value
            blog_page.wait_for_load_state()

            blog_page.close()
            galxe_page.bring_to_front()

            with galxe_page.context.expect_page() as new_page_info:
                galxe_page.get_by_text("Daily Visit the Sahara AI Twitter").click()
            twitter_page = new_page_info.value
            twitter_page.wait_for_load_state()
            twitter_page.close()
            galxe_page.bring_to_front()

            time.sleep(3)

            button_locator = galxe_page.locator(
                'button:has(div.flex.gap-1.items-center svg path[fill="#CED3DB"])'
            ).all()

            logging.info(f"刷新按键数量: {len(button_locator)}")
            if len(button_locator) > 0:
                button_locator[0].click()  # 点击按钮
                time.sleep(3)
                galxe_page.close()

            time.sleep(3)  # 让页面有时间跳转
            return base_page
        except Exception as e:
            logging.error(f"页面加载失败: {e}")

    def trans(self, evm_passwd, context):
        """转账任务 向联系人地址转入随机数量的代币"""

        # 在新上下文中打开MetaMask
        meta_page = context.new_page()
        meta_page.goto("chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html")
        time.sleep(3)
        password_input = meta_page.locator("#password")
        if password_input.count() > 0:
            password_input.fill(evm_passwd)  # 填入密码
            meta_page.click("button:has-text('解鎖')")
            time.sleep(3)

        # 获取最后一个交易成功对象 获取不到就返回
        try:
            meta_page.get_by_text("已確認").all()[0].click()
        except Exception:
            return meta_page
        time.sleep(3)

        # 获取无联系人转账对象地址
        try:
            address = meta_page.locator(
                "p.mm-box.mm-text.name__value.mm-text--body-md.mm-box--color-text-default"
            ).text_content()
            if address.__contains__("0x"):
                meta_page.get_by_text(address).click()
            else:
                address = meta_page.locator(
                    ".sender-to-recipient__tooltip-wrapper .name__name"
                )
                if address.count() > 0:
                    address.wait_for()
                    address.click()
        # 获取联系人转账对象地址
        except Exception:
            address = meta_page.locator(
                ".sender-to-recipient__tooltip-wrapper .name__name"
            )
            if address.count() > 0:
                address.wait_for()
                address.click()
        value = meta_page.locator("#address").input_value()

        # 转账
        meta_page.reload()
        meta_page.locator('button[data-testid="eth-overview-send"]').click()
        meta_page.locator('input[data-testid="ens-input"]').fill(value)
        time.sleep(3)
        meta_page.locator('input[data-testid="currency-input"]').all()[0].fill(
            str("{:.5f}".format(random.uniform(0.00001, 0.00009)))
        )
        meta_page.get_by_text("繼續").click()
        meta_page.get_by_text("確認").click()
        time.sleep(3)
        return meta_page

    def claim(self, base_page):
        """领取碎片"""

        old_amount_value, base_page = self.in_legends(base_page, click_img=True)

        # 进入任务界面 点击刷新按钮
        svg_element = base_page.locator('svg[width="32"][height="32"]')
        buttons_list = svg_element.all()
        base_page.set_default_timeout(100)
        for button in buttons_list:
            try:
                button.click()
            except Exception:
                continue
        time.sleep(3)

        # 点击领取按钮
        claim__all = base_page.get_by_text("claim")
        buttons_list = claim__all.all()
        for button in buttons_list:
            try:
                button.click()
            except Exception:
                continue
        time.sleep(3)

        base_page.set_default_timeout(30000)
        base_page.reload()
        base_page.wait_for_load_state()
        amount_value = base_page.locator("div.amount").text_content()
        oa = int(old_amount_value)
        a = int(amount_value)
        if oa == a:
            sing.log_signal.emit(("ERROR", "领取碎片失败"))
        if (a - oa) == 2:
            sing.log_signal.emit(("ERROR", "转账领取碎片失败"))
        if (a - oa) == 20 or (a - oa) == 21:
            sing.log_signal.emit(("WARNING", "银河领取碎片失败"))
        if (a - oa) == 22:
            sing.log_signal.emit(("SUCCESS", "任务执行完成"))
        return base_page

    def execute_task(
        self,
        base_page: Page,
        user_id: str,
        evm_address: str,
        evm_passwd: str,
        task: str,
    ) -> None:
        if task == "legends":
            self.legends(evm_passwd, base_page)
        elif task == "trans":
            self.trans(evm_passwd, base_page.context)
        elif task == "claim":
            self.claim(base_page)
