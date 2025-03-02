import logging
import time
from functools import lru_cache

from playwright.sync_api import Page

from core.tasks.base_task import BaseTask

GAME_WAIT_TIME = 3


class Newton(BaseTask):
    def _unlock_metamask(self, base_page: Page) -> None:
        """解锁 MetaMask 钱包"""

        try:
            base_page.locator("#password").fill("lqqohiyw3818")
            base_page.click("button:has-text('解鎖')")
            time.sleep(3)
        except Exception as e:
            logging.error(e)

    def _play_game(self, base_page: Page) -> None:
        """执行游戏操作"""
        base_page.get_by_text("Roll now").click()
        time.sleep(GAME_WAIT_TIME)

        try:
            base_page.get_by_text("Let's roll").click()
            time.sleep(GAME_WAIT_TIME)
            base_page.get_by_text("Throw Dice").click()
            time.sleep(3)
        except Exception as e:
            logging.error(e)

    def _make_game_decision(self, base_page: Page) -> None:
        """根据策略做出游戏决策"""
        h2_element = base_page.wait_for_selector("h2.jsx-f1b6ce0373f41d79")
        current = int(h2_element.text_content())

        for turns in range(4, 1, -1):
            want = self.optimal_expected_score(turns, current)
            logging.info(f"当前分数: {current}")
            logging.info(f"期望分数: {want}")

            if want <= current:
                logging.info(f"Bank分数: {current}")
                base_page.locator("button:has-text('Bank')").click()
                time.sleep(GAME_WAIT_TIME)
                break
            else:
                base_page.get_by_role("button", name="Press").click()
                time.sleep(5)
                current = int(
                    base_page.locator("h2.jsx-f1b6ce0373f41d79").text_content()
                )
            time.sleep(GAME_WAIT_TIME)

    def roll(self, base_page: Page) -> None:
        """执行完整的游戏流程"""

        base_page.goto("chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html")
        # 等待扩展加载
        time.sleep(5)

        self._unlock_metamask(base_page)
        base_page.set_viewport_size({"width": 1920, "height": 1080})

        # 进入游戏
        base_page.goto("https://www.magicnewton.com/portal")
        time.sleep(GAME_WAIT_TIME * 2)  # 增加等待时间

        # 执行游戏
        self._play_game(base_page)
        self._make_game_decision(base_page)
        time.sleep(GAME_WAIT_TIME)

    @lru_cache(maxsize=None)
    def optimal_expected_score(self, turns_left: int, current_score: int) -> float:
        """计算最优期望分数"""
        if turns_left == 0:
            return current_score

        stop_value = current_score

        # 计算继续游戏的期望值
        add_expected = (
            sum(
                self.optimal_expected_score(turns_left - 1, current_score + k)
                for k in range(1, 31)
            )
            / 30
        )

        double_expected = self.optimal_expected_score(turns_left - 1, current_score * 2)
        half_expected = self.optimal_expected_score(turns_left - 1, current_score / 2)

        continue_expected = (add_expected + double_expected + half_expected) / 4

        return max(stop_value, continue_expected)

    def execute_task(
        self,
        base_page: Page,
        user_id: str,
        evm_address: str,
        evm_passwd: str,
        task: str,
    ) -> None:
        if task == "roll":
            self.roll(base_page)
