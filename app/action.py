import re
import requests
import urllib3
import hashlib

urllib3.disable_warnings()


def get_md5_hash(s):
    md5_hash = hashlib.md5()
    md5_hash.update(s.encode('utf-8'))
    return md5_hash.hexdigest()

def extract_csrf_token(string):
    pattern = r"csrfToken:\s*'(\w+)'"
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        return None

def extract_score_info(string):
    today_pattern = r'今日签到获得\s*<code>(\d+)</code>\s*积分'
    all_pattern = r'积分余额\s*(\d+)'
    today_match = re.search(today_pattern, string)
    all_match = re.search(all_pattern, string)
    if today_match != None and all_match != None:
        return int(today_match.group(1)), int(all_match.group(1))
    return ()


class Action:
    def __init__(self, username: str, passwd: str, host: str, login_path: str, token_path: str, checkin_path: str):
        self.username = username
        self.passwd = get_md5_hash(passwd)
        self.host = host.replace('https://', '').replace('http://', '').strip()
        self.login_path = login_path
        self.token_path = token_path
        self.checkin_path = checkin_path
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Edge/108.0.2088.61'
        }
        self.timeout = 6

    def format_url(self, path) -> str:
        return f'https://{self.host}/{path}'

    def login(self) -> dict:
        login_url = self.format_url(self.login_path)
        form_data = {
            'userName': self.username,
            'userPassword': self.passwd,
        }
        return self.session.post(login_url, json=form_data, headers=self.headers,
                                 timeout=self.timeout, verify=False).json()

    def get_csrf_token(self, get_score=False):
        token_url = self.format_url(self.token_path)
        res = self.session.get(token_url, headers=self.headers, timeout=self.timeout, verify=False)
        self.csrf_token = extract_csrf_token(res.text)
        if get_score:
            return extract_score_info(res.text)
        return self.csrf_token

    def checkin(self) -> dict:
        checkin_url = self.format_url(self.checkin_path)
        data = {
            'token': self.csrf_token,
            'v': 2
        }
        headers = {
            'User-Agent': 'Edge/108.0.2088.61',
            'Referer': self.format_url(self.token_path)
        }
        res = self.session.get(checkin_url, params=data, headers=headers, timeout=self.timeout, verify=False)
        if res.status_code == 200:
            return True
        return False

    def run(self):
        self.login()
        self.get_csrf_token()
        self.checkin()
        self.get_csrf_token(True)
