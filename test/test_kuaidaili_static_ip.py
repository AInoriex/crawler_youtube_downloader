#!/usr/bin/env Python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests

secret_id = 'o77rahiirdmx5udc4eaw'
secret_key = 'j7ilksthul2dz1pvagnbr0j80s2fxh9z'
SECRET_PATH = 'cache/kuaidaili.token'

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


def reqeust_test():
    """
    使用requests请求代理服务器
    请求http和https网页均适用
    """
    sid = "o77rahiirdmx5udc4eaw"
    sign = "ojuve99qobf49psjkjcfwymci4"
    # 提取代理API接口
    # api_url = f"http://dps.kdlapi.com/api/getdps/?secret_id={sid}&signature={sign}&num=1&pt=1&sep=1"
    # 获取API接口返回的代理IP
    # proxy_ip = requests.get(api_url).text

    # proxy_ip = "149.40.87.140:2333:cgjhx9jxn3xy:piez4h5uesrv:US"
    # proxy_ip = "149.40.87.140"
    proxy_ip = "149.40.87.140:2333"

    # 用户名密码认证(私密代理/独享代理)
    username = "cgjhx9jxn3xy"
    password = "piez4h5uesrv"
    # username = "sf2883489273"
    # password = "jh2n65ma"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
    }

    # 白名单方式（需提前设置白名单）
    # proxies = {
    #     "http": "http://%(proxy)s/" % {"proxy": proxy_ip},
    #     "https": "http://%(proxy)s/" % {"proxy": proxy_ip}
    # }

    # 要访问的目标网页
    target_url = "https://dev.kdlapi.com/testproxy"
    # target_url = "https://ip.sb"

    # 使用代理IP发送请求
    response = requests.get(target_url, proxies=proxies)

    # 获取页面内容
    if response.status_code == 200:
        print(response.text)


if __name__ == '__main__':
    # secret_token = get_secret_token()
    # print(secret_token)

    reqeust_test()
