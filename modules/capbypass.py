import json
import time

import loguru
import requests


class Solver:
    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def solve(self, blob, proxy) -> str | bool:
        user, user_port, ip, ip_port = proxy.replace("@", ":").split(":") #matthew please fix this format lol
        formatted_proxy = f"{ip}:{ip_port}:{user}:{user_port}"
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "FunCaptchaTask",
                "websiteURL": "https://www.roblox.com",
                "websitePublicKey": "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F",
                "websiteSubdomain": "https://roblox-api.arkoselabs.com",
                "proxy": formatted_proxy,
                "data": json.dumps({"blob": blob}),
                "headers": {
                    "acceptLanguage": "en-GB,en;q=0.9",
                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                }
            }
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post("https://capbypass.com/api/createTask", json=payload, headers=headers)
        task_id = response.json()["taskId"]

        while True:
            response = requests.post("https://capbypass.com/api/getTaskResult", json={
                "clientKey": self.api_key,
                "taskId": task_id
            },headers=headers)
            if response.json()["status"] == "FAILED":
                loguru.logger.error("Failed to solve captcha: {}".format(response.json()["errorDescription"]))
                return False
            elif response.json()["status"] == "DONE":
                loguru.logger.info(f"Solved captcha: {response.json()['solution'][:60]}..")
                return response.json()["solution"]
            time.sleep(1)

