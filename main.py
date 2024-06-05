import re
import json
import time
import random
import base64
import loguru
import requests
import threading
import random_strings

import modules.capbypass
import modules.mailtm as mailtm
from datetime import datetime, timezone
from random_username.generate import generate_username

settings_json = json.loads(open("settings.json", "r").read())



class RobloxGen:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "authority": "www.roblox.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "pragma": "no-cache",
            "sec-ch-ua": '"Not_A Brand";v="9", "Chromium";v="125", "Brave";v="125"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        self.proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
        self.session.proxies = {
            "http": "http://" + self.proxy.strip(),
            "https": "http://" + self.proxy.strip(),
        }
        self.mailapi = mailtm.MailTM()
        maildetails = self.mailapi.create_account(self.mailapi.get_domain())

        self.mail = maildetails["mail"]
        self.mailpassword = maildetails["password"]

        self.account_passw = random_strings.random_string(12)

    def get_csrf(self):
        self.session.headers["authority"] = "www.roblox.com"
        response = self.session.get("https://www.roblox.com/home")

        self.csrf_token = response.text.split('"csrf-token" data-token="')[1].split(
            '"'
        )[0]
        self.session.headers["x-csrf-token"] = self.csrf_token

    def generate_birthday(self):
        birthdate = (
            datetime(
                random.randint(1990, 2006),
                random.randint(1, 12),
                random.randint(1, 28),
                21,
                tzinfo=timezone.utc,
            )
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
        return birthdate

    def verify_username(self):
        self.session.headers["authority"] = "auth.roblox.com"
        self.session.headers["accept"] = "application/json, text/plain, */*"

        self.birthdate = self.generate_birthday()
        nickname = generate_username(1)[0]+str(random.randint(10,99))

        response = self.session.get(
            f"https://auth.roblox.com/v1/validators/username?Username={nickname}&Birthday={self.birthdate}",
        )
        try:
            self.nickname = random.choice(response.json()["suggestedUsernames"])
        except:
            self.nickname = nickname
    def purchase_free_items(self):
        params = {
            'category': 'Characters',
            'minPrice': '0',
            'maxPrice': '0',
            'salesTypeFilter': '1',
            'limit': '120',
        }

        response = self.session.get('https://catalog.roblox.com/v1/search/items', params=params)
        random_character = random.choice(response.json()["data"])["id"]

        for a in range(2): # sometimes even if we buy it once, it doesn't fall into inventory:
            self.random_character_id  = self.session.get(f'https://catalog.roblox.com/v1/bundles/details?bundleIds[]={random_character}').json()[0]["product"]["id"]


            csrf_token = self.session.get(f'https://www.roblox.com/bundles/{random_character}').text.split('"csrf-token" data-token="')[1].split('"')[0]
            self.session.headers['x-csrf-token'] = csrf_token

            json_data = {
                'expectedPrice': 0,
            }

            response = self.session.post(
                f'https://economy.roblox.com/v1/purchases/products/{self.random_character_id}',
                json=json_data,
            )
            if response.json()["purchased"]:
                self.assetname = response.json()['assetName']
        loguru.logger.success(f"[{self.assetname}] bundle purchased!")


    def humanize_avatar(self):
        self.purchase_free_items()

        csrftkn = self.session.get('https://www.roblox.com/my/avatar').text.split('"csrf-token" data-token="')[1].split('"')[0]

        self.session.headers['authority'] = 'accountsettings.roblox.com'
        self.session.headers['x-csrf-token'] = csrftkn
        self.session.headers['x-bound-auth-token'] = 'pro-roblox-uhq-encrypted'

        for a in range(2): #same bug as purchase:
            params = {
                'isEditable': 'false',
                'itemsPerPage': '50',
                'outfitType': 'Avatar',
            }
            response = self.session.get(
                f'https://avatar.roblox.com/v2/avatar/users/{self.userid}/outfits',
                params=params,
            )
            outfit_id = response.json()["data"][0]["id"]

            response = self.session.get(f'https://avatar.roblox.com/v1/outfits/{outfit_id}/details')

            assets = response.json()["assets"]
            bodyscale = response.json()["scale"]
            playerAvatarType = response.json()["playerAvatarType"]

            json_data = {
                'height': int(bodyscale['height']),
                'width': int(bodyscale['width']),
                'head': int(bodyscale['head']),
                'depth': int(bodyscale['depth']),
                'proportion': int(bodyscale['proportion']),
                'bodyType': int(bodyscale['bodyType']),
            }

            response = self.session.post('https://avatar.roblox.com/v1/avatar/set-scales',
                                     json=json_data)

            json_data = {
                'assets':assets
            }

            response = self.session.post(
                'https://avatar.roblox.com/v2/avatar/set-wearing-assets',
                json=json_data,
            )

            json_data = {
                'playerAvatarType': playerAvatarType,
            }

            response = self.session.post(
                'https://avatar.roblox.com/v1/avatar/set-player-avatar-type',
                json=json_data,
            )
        loguru.logger.success(f"[{self.mail}] avatar applied!")

        csrftkn = self.session.get(f"https://www.roblox.com/users/{self.userid}/profile").text.split('"csrf-token" data-token="')[1].split('"')[0]

        self.session.headers['x-csrf-token'] = csrftkn

        data = {
            'description': random.choice(open("bio.txt","r",encoding="utf-8").readlines()).strip(),
        }

        response = self.session.post('https://users.roblox.com/v1/description', data=data)
        loguru.logger.success(f"[{self.mail}] bio applied, humanization finished!")


    def signup_request(self):
        json_data = {
            "username": self.nickname,
            "password": self.account_passw,
            "birthday": self.birthdate,
            "gender": 2,
            "isTosAgreementBoxChecked": True,
            "agreementIds": [
                "adf95b84-cd26-4a2e-9960-68183ebd6393",
                "91b2d276-92ca-485f-b50d-c3952804cfd6",
            ],
            "secureAuthenticationIntent": {
                "clientPublicKey": "roblox sucks",
                "clientEpochTimestamp": str(time.time()).split(".")[0],
                "serverNonce": self.serverNonce,
                "saiSignature": "lol",
            },
        }

        response = self.session.post(
            "https://auth.roblox.com/v2/signup", json=json_data
        )

        return response

    def generate_account(self):
        self.session.headers["authority"] = "apis.roblox.com"
        response = self.session.get(
            "https://apis.roblox.com/hba-service/v1/getServerNonce"
        )
        self.serverNonce = response.text.split('"')[1]

        self.session.headers["authority"] = "auth.roblox.com"

        response = self.signup_request()

        if "Token Validation Failed" in response.text:
            self.session.headers["x-csrf-token"] = response.headers["x-csrf-token"]
            response = self.signup_request()
        if response.status_code == 429:
            loguru.logger.error("ip ratelimit, retrying..")
            return ""
        captcha_response = json.loads(
            base64.b64decode(
                response.headers["rblx-challenge-metadata"].encode()
            ).decode()
        )
        unifiedCaptchaId = captcha_response["unifiedCaptchaId"]
        dataExchangeBlob = captcha_response["dataExchangeBlob"]
        genericChallengeId = captcha_response["sharedParameters"]["genericChallengeId"]

        solver = modules.capbypass.Solver(settings_json["capbypass_key"])
        captcha_solution = solver.solve(dataExchangeBlob, self.proxy)
        if captcha_solution == False:
            return ""

        self.session.headers["authority"] = "apis.roblox.com"

        json_data = {
            "challengeId": genericChallengeId,
            "challengeType": "captcha",
            "challengeMetadata": json.dumps(
                {
                    "unifiedCaptchaId": genericChallengeId,
                    "captchaToken": captcha_solution,
                    "actionType": "Signup",
                }
            ),
        }

        self.session.post(
            "https://apis.roblox.com/challenge/v1/continue", json=json_data
        )

        self.session.headers["rblx-challenge-id"] = unifiedCaptchaId
        self.session.headers["rblx-challenge-type"] = "captcha"
        self.session.headers["rblx-challenge-metadata"] = base64.b64encode(
            json.dumps(
                {
                    "unifiedCaptchaId": unifiedCaptchaId,
                    "captchaToken": captcha_solution,
                    "actionType": "Signup",
                }
            ).encode()
        ).decode()

        resp = self.signup_request()
        try:
            cookie = resp.cookies[".ROBLOSECURITY"]
        except:
            loguru.logger.error("capbypass gives us wrong captcha token 😡..")
            return ""
        self.userid = resp.json()["userId"]
        loguru.logger.info(f"[https://www.roblox.com/users/{self.userid}] account created!")

        del self.session.headers["rblx-challenge-id"]
        del self.session.headers["rblx-challenge-type"]
        del self.session.headers["rblx-challenge-metadata"]

        self.get_csrf()
        self.session.headers["authority"] = "accountsettings.roblox.com"

        json_data = {
            "emailAddress": self.mail,
        }

        response = self.session.post(
            "https://accountsettings.roblox.com/v1/email", json=json_data
        )
        if response.status_code == 200:
            loguru.logger.info(f"[{self.userid}] mail set as {self.mail}")

            if settings_json["verify_mail"]:
                self.mailtoken = self.mailapi.get_account_token(
                    self.mail, self.mailpassword
                )
                mail_timeout = 0
                while True:
                    mail_timeout += 1
                    time.sleep(1)

                    mailboxdetails = self.mailapi.get_mail(self.mailtoken)
                    if mailboxdetails["hydra:member"] != []:
                        message_id = mailboxdetails["hydra:member"][0]["id"]

                        mailcontent = self.mailapi.get_mail_content(
                            self.mailtoken, message_id
                        )

                        ticketid = re.search(r"http[s]*\S+", mailcontent["text"])[0].split("?ticket=")[1]

                        json_data = {
                            "ticket": ticketid.strip(),
                        }

                        response = self.session.post(
                            "https://accountinformation.roblox.com/v1/email/verify",
                            json=json_data,
                        )
                        loguru.logger.info(
                            f"[{self.mail}] mail verified and free prize claimed! - https://www.roblox.com/catalog/{response.json()['verifiedUserHatAssetId']}"
                        )
                        break

                    if mail_timeout == 30:
                        loguru.logger.error(f"[{self.mail}] mail timeout, skipping..")
                        return ""
            else:
                loguru.logger.warning(f"[{self.mail}] mail verification skipping..")

        else:
            loguru.logger.error(f"[{self.mail}] cant set mail! {response.text}")

        if settings_json["humanize"]:
            self.humanize_avatar()
        else:
            loguru.logger.warning(f"[{self.mail}] humanizing skipping..")


        loguru.logger.success(f"[{self.mail}] account saved into txt!")
        open("accounts.txt", "a").write(
            f"{self.nickname}:{self.account_passw}:{self.mail}:{self.mailpassword}:{cookie}\n"
        )


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


proxy = open("proxy.txt", "r").readlines()
if proxy == []:
    loguru.logger.error("proxy.txt is empty, fill it with proxies.")
    exit()


def main():
    thread_count = settings_json["thread_count"]
    total_generate_count = int(input("How many accounts do you want to gen > "))
    generate_per_thread = total_generate_count / thread_count
    if total_generate_count % thread_count != 0:
        loguru.logger.error(
            "set the total number of accounts to be created divided by the number of threads to 0"
        )
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


if __name__ == "__main__":
    main()
