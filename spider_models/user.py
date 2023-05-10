import json
import logging
import pickle
import re
import time
from urllib import parse

import qrcode
import requests
from requests import cookies
from requests import utils

from models.user_picked import UserPicked


class User(object):
    user_list = []

    def __init__(self):
        self.last_replied = 0
        self.password = None
        self.mobile = None
        self.headers = {
            'Sec-Ch-Ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/112.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'X-Client-Locale': 'zh-CN',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Origin': 'https://www.zfrontier.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.cookie = None
        self.nickname = None
        self.id = None
        self.session = None
        User.user_list.append(self)

    def pickle_self(self):
        try:
            logging.info(f"pickle {self.id}-{self.nickname} success!")
            serialized_class = pickle.dumps(self)
            UserPicked.update(data=serialized_class).where(UserPicked.id == self.id).execute()
        except Exception as e:
            logging.error(e)

    def login_with_passwd(self, mobile, password):
        password_url = 'https://www.zfrontier.com/api/login/mobile'
        session = requests.session()
        self.session = session
        self.get_csrf_token()
        data = {
            'mobile': mobile,
            'password': password
        }
        login_res = session.post(url=password_url, headers=self.headers, data=data)
        if '"ok":0' in login_res.text:
            logging.info(f"login {self.id}-{self.nickname} success!")
            cookie_dict = requests.utils.dict_from_cookiejar(login_res.cookies)
            new_cookies = requests.cookies.RequestsCookieJar()
            new_cookies.update(cookie_dict)
            self.get_csrf_token()
            self.id = re.search(r'userId%22%3A(\d+)%2C%22hashId', new_cookies['userDisplayInfo']).group(1)
            self.nickname = parse.unquote(re.search(r'nickname%22%3A%22([^\"]+)%22%2C%22avatarPath',
                                                    new_cookies['userDisplayInfo']).group(1))
            self.cookie = new_cookies
            self.session = session
            self.mobile = mobile
            self.password = password
            if UserPicked.select().where(UserPicked.id == self.id).exists():
                UserPicked.update(nickname=self.nickname, mobile=self.mobile, password=self.password,
                                  status=True).where(UserPicked.id == self.id).execute()
            else:
                UserPicked.create(id=self.id, nickname=self.nickname, mobile=self.mobile, password=self.password,
                                  status=True)
        else:
            logging.info(f"login {self.id}-{self.nickname} false!")

    def login(self):
        start_url = 'https://www.zfrontier.com/login/ajaxAppProxyStart'
        session = requests.session()
        self.session = session
        self.get_csrf_token()
        res = session.post(url=start_url, headers=self.headers)
        if 'success' in res.text:
            start_json = json.loads(res.text)
            qr_url = start_json['data']['qrURL']
            check_url = 'https://' + start_json['data']['checkURL'][2:]
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.show()
            while True:
                login_res = session.post(url=check_url, headers=self.headers)
                if '"ok":0' in login_res.text:
                    logging.info(f"login {self.id}-{self.nickname} success!")
                    cookie_dict = requests.utils.dict_from_cookiejar(login_res.cookies)
                    new_cookies = requests.cookies.RequestsCookieJar()
                    new_cookies.update(cookie_dict)
                    self.get_csrf_token()
                    break
                time.sleep(2)
            res_json = json.loads(login_res.text)
            self.id = res_json['data']['user_info']['id']
            self.nickname = res_json['data']['user_info']['nickname']
            self.cookie = new_cookies
            self.session = session
            if UserPicked.select().where(UserPicked.id == self.id).exists():
                UserPicked.update(nickname=self.nickname, status=True).where(UserPicked.id == self.id).execute()
            else:
                UserPicked.create(id=self.id, nickname=self.nickname, status=True)
        else:
            logging.info(f"login {self.id}-{self.nickname} false!")

    def get_csrf_token(self):
        try:
            csrf_url = 'https://www.zfrontier.com/app/'
            res = self.session.get(url=csrf_url, headers=self.headers)
            match = re.search(r"dow\.csrf_token = '(.+?)';", res.text)
            self.headers['X-Csrf-Token'] = match.group(1)
            logging.info(f"{self.id}-{self.nickname} got csrf-token")
        except Exception as e:
            logging.error(e)

    def reply(self, post_id):
        url = 'https://www.zfrontier.com/v2/flow/reply'
        data = {
            'id': post_id,
            'reply_id': '',
            'content': '<p>冲冲冲</p>',
        }
        try:
            res = self.session.post(url=url, data=data, headers=self.headers, cookies=self.cookie)
            if '"ok":0' in res.text:
                self.last_replied = post_id
                logging.info(f"{self.id}-{self.nickname} replied {post_id}")
                UserPicked.update(last_replied=post_id).where(UserPicked.id == self.id).execute()
            else:
                try:
                    logging.warning(f"try to re-login {self.id}-{self.nickname}")
                    this_user = UserPicked.select().where(UserPicked.id == self.id).execute()
                    mobile = this_user.mobile
                    password = this_user.password
                    self.login_with_passwd(mobile, password)
                    logging.info(f"re-login {self.id}-{self.nickname} success!")
                except Exception as e:
                    logging.warning(e)
                    UserPicked.update(status=False).where(UserPicked.id == self.id).execute()
        except Exception as e:
            logging.error(e)

    def get_msg(self, startId=0):
        msg_url = 'https://www.zfrontier.com/v2/notifies'
        data = {
            'startId': startId
        }
        try:
            res = self.session.post(url=msg_url, data=data,headers=self.headers,cookies=self.cookie)
            res_dict = json.loads(res.text)
            logging.info(f"get msgs of {self.nickname}:{res_dict}")
            has_more = res_dict["data"]["hasMore"]
            msg_list = res_dict["data"]["list"]
            msgs = list()
            for i in msg_list:
                msgs.append(i["html"])
            if has_more:
                startId = msg_list[-1]["id"]
                msgs.append(self.get_msg(startId))
            logging.info(f"get msg {self.id}-{self.nickname} success!")
        except Exception as e:
            logging.error(e)
            msgs=[]
        return msgs
