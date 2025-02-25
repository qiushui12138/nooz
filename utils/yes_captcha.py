import time

import requests

from config.config import custom_config


class YesCaptcha:
    def __init__(self):
        self.key = custom_config.get_yes_captcha_key()
        self.captcha_url = "https://api.yescaptcha.com"

    def solve_hcaptcha_with_yescaptcha(self, url, site_key, user_agent):
        """使用 YesCaptcha 解决 hCaptcha"""

        # 1. 发送验证码请求
        create_task_payload = {
            "clientKey": self.key,
            "task": {
                "websiteURL": url,
                "websiteKey": site_key,
                "type": "HCaptchaTaskProxyless",
                "userAgent": user_agent,
                "isInvisible": False,
            },
        }
        create_task_response = requests.post(
            f"{self.captcha_url}/createTask", json=create_task_payload
        )
        task_data = create_task_response.json()
        if "taskId" not in task_data:
            raise ValueError("hCaptcha 任务创建失败")
        task_id = task_data["taskId"]

        # 2. 轮询验证码结果（超时时间 2 分钟）
        timeout = time.time() + 120
        while time.time() < timeout:
            get_result_payload = {"clientKey": self.key, "taskId": task_id}
            get_result_response = requests.post(
                f"{self.captcha_url}/getTaskResult", json=get_result_payload
            )
            result = get_result_response.json()
            if result.get("status") == "ready":
                captcha_solution = result["solution"]["gRecaptchaResponse"]
                print(f"hCaptcha 解析完成: {captcha_solution[:20]}...")
                return captcha_solution
            print("等待 hCaptcha 解析...")
            time.sleep(5)
        else:
            raise TimeoutError("hCaptcha 解析超时")
