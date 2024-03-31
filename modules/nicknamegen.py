import requests


class NicknameGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "authority": "nicknamemaker.net",
            "accept": "*/*",
            "accept-language": "tr-TR,tr;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://nicknamemaker.net",
            "pragma": "no-cache",
            "referer": "https://nicknamemaker.net/",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

    def generate_nickname(self):
        data = {
            "nickid": "5467362",
            "nickword": "rerelyoti",
            "nickname": "rerelyoti",
            "words": "1",
            "language": "en",
            "length": "12",
            "beginswith": "",
            "endswith": "",
        }

        response = self.session.post(
            "https://nicknamemaker.net/index.php?ldr=main&fn=nickname&arg[0]=65a9937d06322&xhr=1705612158487",
            data=data,
        )
        return response.json()["data"]["nickword"]
