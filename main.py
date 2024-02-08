import base64
import json
import random
import threading
import time
from datetime import datetime, timezone

import capsolver
import loguru
import random_strings

import modules.nicknamegen
import modules.mailtm
import requests

settings_json = json.loads(open("settings.json", "r").read())

capsolver.api_key = settings_json["capsolver_key"]


class RobloxGen:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'authority': 'www.roblox.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'tr-TR,tr;q=0.7',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        self.proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
        self.session.proxies = {'http': 'http://' + self.proxy.strip(), 'https': 'http://' + self.proxy.strip()}
        self.mailapi = modules.mailtm.MailTM()
        self.mail = self.mailapi.create_account(self.mailapi.get_domain())["mail"]
        self.account_passw = random_strings.random_string(12)

    def get_csrf(self):
        self.session.headers['authority'] = 'www.roblox.com'
        response = self.session.get('https://www.roblox.com/home')

        self.csrf_token = response.text.split('"csrf-token" data-token="')[1].split('"')[0]
        self.session.headers['x-csrf-token'] = self.csrf_token

    def generate_birthday(self):
        birthdate = datetime(random.randint(1990, 2006), random.randint(1, 12), random.randint(1, 28), 21,
                             tzinfo=timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
        return birthdate

    def verify_username(self):
        self.session.headers['authority'] = 'auth.roblox.com'
        self.session.headers['accept'] = 'application/json, text/plain, */*'

        self.birthdate = self.generate_birthday()
        nickname = modules.nicknamegen.NicknameGenerator().generate_nickname()

        response = self.session.get(
            f'https://auth.roblox.com/v1/validators/username?Username={nickname}&Birthday={self.birthdate}',
        )
        try:
            self.nickname = random.choice(response.json()["suggestedUsernames"])
        except:
            self.nickname = nickname

    def signup_request(self):

        json_data = {
            'username': self.nickname,
            'password': self.account_passw,
            'birthday': self.birthdate,
            'gender': 2,
            'isTosAgreementBoxChecked': True,
            'agreementIds': [
                'adf95b84-cd26-4a2e-9960-68183ebd6393',
                '91b2d276-92ca-485f-b50d-c3952804cfd6',
            ],
            'secureAuthenticationIntent': {
                'clientPublicKey': 'roblox sucks',
                'clientEpochTimestamp': str(time.time()).split(".")[0],
                'serverNonce': self.serverNonce,
                'saiSignature': 'lol',
            },
        }

        response = self.session.post('https://auth.roblox.com/v2/signup', json=json_data)

        return response

    def generate_account(self):
        self.session.headers['authority'] = 'apis.roblox.com'
        response = self.session.get('https://apis.roblox.com/hba-service/v1/getServerNonce')
        self.serverNonce = response.text.split('"')[1]

        self.session.headers['authority'] = 'auth.roblox.com'

        response = self.signup_request()

        if "Token Validation Failed" in response.text:
            self.session.headers['x-csrf-token'] = response.headers["x-csrf-token"]
            response = self.signup_request()
        captcha_response = json.loads(base64.b64decode(response.headers["rblx-challenge-metadata"].encode()).decode())
        unifiedCaptchaId = captcha_response["unifiedCaptchaId"]
        dataExchangeBlob = captcha_response["dataExchangeBlob"]
        genericChallengeId = captcha_response["sharedParameters"]["genericChallengeId"]

        try:
            captcha_solution = capsolver.solve({
                "type": "FunCaptchaTask",
                "websiteURL": "https://www.roblox.com",
                "websitePublicKey": "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F",
                "funcaptchaApiJSSubdomain": "https://roblox-api.arkoselabs.com",
                "data": "{\"blob\":\"" + dataExchangeBlob + "\"}",
                "proxy":"http://"+self.proxy
            })["token"]
        except Exception as E:
            loguru.logger.error(f"capsolver can't solve captcha.. {E}")
            return ""

        self.session.headers["authority"] = "apis.roblox.com"

        json_data = {
            'challengeId': genericChallengeId,
            'challengeType': 'captcha',
            'challengeMetadata': json.dumps(
                {"unifiedCaptchaId": genericChallengeId, "captchaToken": captcha_solution, "actionType": "Signup"}),
        }

        self.session.post('https://apis.roblox.com/challenge/v1/continue', json=json_data)

        self.session.headers['rblx-challenge-id'] = unifiedCaptchaId
        self.session.headers['rblx-challenge-type'] = 'captcha'
        self.session.headers['rblx-challenge-metadata'] = base64.b64encode(json.dumps(
            {"unifiedCaptchaId": unifiedCaptchaId, "captchaToken": captcha_solution,
             "actionType": "Signup"}).encode()).decode()

        resp = self.signup_request()
        cookie = resp.cookies['.ROBLOSECURITY']
        userid = resp.json()['userId']
        loguru.logger.success(f"[https://www.roblox.com/users/{userid}] account created!")

        del self.session.headers['rblx-challenge-id']
        del self.session.headers['rblx-challenge-type']
        del self.session.headers['rblx-challenge-metadata']

        self.get_csrf()
        self.session.headers['authority'] = 'accountsettings.roblox.com'

        json_data = {
            'emailAddress': self.mail,
        }

        response = self.session.post('https://accountsettings.roblox.com/v1/email',
                                     json=json_data)
        if response.status_code == 200:
            loguru.logger.info(f"[{userid}] mail set as {self.mail}")
            open("accounts.txt", "a").write(f"{self.nickname}:{self.account_passw}:{self.mail}:{cookie}\n")
        else:
            loguru.logger.error(f"[{userid}] cant set mail! {response.text}")
            open("accounts.txt", "a").write(f"{self.nickname}:{self.account_passw}:CANT_SET_MAIL:{cookie}\n")


def generate():
    while True:
        try:
            gen = RobloxGen()
            gen.get_csrf()
            gen.verify_username()
            gen.generate_account()
            break
        except KeyError as E:
            loguru.logger.error(f"{E},retrying.")
            pass
        except Exception as E:
            loguru.logger.error(E)
            break


def main():
    thread_count = settings_json["thread_count"]
    total_generate_count = int(input("How many accounts do you want to gen > "))
    generate_per_thread = total_generate_count / thread_count
    if total_generate_count % thread_count != 0:
        loguru.logger.error("set the total number of accounts to be created divided by the number of threads to 0")
        exit()

    for a in range(int(generate_per_thread)):
        threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=generate)
            threads.append(t)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


if __name__ == '__main__':
    main()
