import requests

def reqeust_test():
    """
    使用requests请求代理服务器
    请求http和https网页均适用
    """
    proxy_ip = "149.40.87.140:2333"
    username = "cgjhx9jxn3xy"
    password = "piez4h5uesrv"
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
    # target_url = "https://dev.kdlapi.com/testproxy"
    # target_url = "https://ip.sb"
    target_url = "https://ipinfo.io"

    # 使用代理IP发送请求
    response = requests.get(target_url, proxies=proxies)

    # 获取页面内容
    if response.status_code == 200:
        print(response.status_code, response.text)


if __name__ == '__main__':
    reqeust_test()