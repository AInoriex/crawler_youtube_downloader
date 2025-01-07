#!/usr/bin/env Python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests

secret_id = 'os2gaty4choft041eixx'
secret_key = 'w3yrjphoz352ycjr07jc5ky1lvy28nla'
SECRET_PATH = './.secret'


def _get_secret_token():
    r = requests.post(url='https://auth.kdlapi.com/api/get_secret_token', data={'secret_id': secret_id, 'secret_key': secret_key})
    if r.status_code != 200:
        raise KdlException(r.status_code, r.content.decode('utf8'))
    res = json.loads(r.content.decode('utf8'))
    code, msg = res['code'], res['msg']
    if code != 0:
        raise KdlException(code, msg)
    secret_token = res['data']['secret_token']
    expire = str(res['data']['expire'])
    _time = '%.6f' % time.time()
    return secret_token, expire, _time


def _read_secret_token():
    with open(SECRET_PATH, 'r') as f:
        token_info = f.read()
    secret_token, expire, _time, last_secret_id = token_info.split('|')
    if float(_time) + float(expire) - 3 * 60 < time.time() or secret_id != last_secret_id:  # 还有3分钟过期或SecretId变化时更新
        secret_token, expire, _time = _get_secret_token()
        with open(SECRET_PATH, 'w') as f:
            f.write(secret_token + '|' + expire + '|' + _time + '|' + secret_id)
    return secret_token


def get_secret_token():
    if os.path.exists(SECRET_PATH):
        secret_token = _read_secret_token()
    else:
        secret_token, expire, _time = _get_secret_token()
        with open(SECRET_PATH, 'w') as f:
            f.write(secret_token + '|' + expire + '|' + _time + '|' + secret_id)
    return secret_token


class KdlException(Exception):
    """异常类"""

    def __init__(self, code=None, message=None):
        self.code = code
        if sys.version_info[0] < 3 and isinstance(message, unicode):
            message = message.encode("utf8")
        self.message = message
        self._hint_message = "[KdlException] code: {} message: {}".format(self.code, self.message)

    @property
    def hint_message(self):
        return self._hint_message

    @hint_message.setter
    def hint_message(self, value):
        self._hint_message = value

    def __str__(self):
        if sys.version_info[0] < 3 and isinstance(self.hint_message, unicode):
            self.hint_message = self.hint_message.encode("utf8")
        return self.hint_message


def test_tunnel_request():
    """
    使用requests请求隧道服务器
    请求http和https网页均适用
    """

    import requests

    # 隧道域名:端口号
    # tunnel = "tpsXXX.kdlapi.com:15818"
    # tunnel = "g737.kdlfps.com:18866" # 全球转发
    tunnel = "us.g737.kdlfps.com:18866" # 美洲区域
    # tunnel = "as.g737.kdlfps.com:18866" # 亚洲区域

    # 用户名密码方式
    username = "f2269754536"
    password = "6qquedym"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }

    # 白名单方式（需提前设置白名单）
    # proxies = {
    #     "http": "http://%(proxy)s/" % {"proxy": tunnel},
    #     "https": "http://%(proxy)s/" % {"proxy": tunnel}
    # }

    # 要访问的目标网页
    target_url = "https://dev.kdlapi.com/testproxy"

    # 使用隧道域名发送请求
    response = requests.get(target_url, proxies=proxies)
    

if __name__ == '__main__':
    secret_token = get_secret_token()
    print(secret_token)