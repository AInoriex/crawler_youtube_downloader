from fake_useragent import UserAgent
from random import choice, randint
import urllib.request as request

def get_random_ua():
    """
    Generates a random User-Agent based on a random OS and browser
    
    The random OS can be one of Windows, macOS, or Linux.
    The random browser can be one of safari, firefox, edge (on Windows), or chrome (on Windows or macOS).
    
    Returns a dictionary with three keys: "os", "browser", and "ua", containing the random OS, browser, and User-Agent, respectively.
    """
    os_list = ["Windows", "macOS", "Linux"]
    operate_sys = choice(os_list)
    # print(f"随机os > {operate_sys}")
    browsers_list = ['safari', 'firefox']
    if operate_sys == "Windows":
        browsers_list.append("edge")
    if operate_sys != 'Linux':
        browsers_list.append("chrome")
    br = choice(browsers_list)
    # print(f"随机browser > {br}")
    ua = UserAgent(browsers=[br.lower()], os=[operate_sys.lower()])
    user_agent = ua.random
    # print(f"随机生成的User-Agent: {user_agent}")
    return {
        "os": operate_sys,
        "browser": br,
        "ua": user_agent
    }

def download_resource(url:str, filename:str, proxies=None):
    """
    使用代理服务器从url处下载文件到本地的filename

    :param url: 要下载的文件的url
    :param filename: 保存到本地的文件名
    :return: None
    """
    print(f"download_resource > 参数：{url} -- {filename}")
    if url == "" or filename == "":
        raise ValueError(f"download_resource url or filename is empty, url:{url}, filename:{filename}")
    ua = get_random_ua()
    headers = [
        ('accept-language','zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6'),
        ('cache-control','no-cache'),
        ('sec-ch-ua','"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"'),
        ('sec-ch-ua-mobile','?0'),
        ('sec-fetch-dest','empty'),
        ('sec-fetch-mode','cors'),
        ('sec-fetch-site','same-origin'),
        ('sec-ch-ua-platform',ua.get('os')),
        ('user-agent',ua.get('ua')),
    ]

    def reporthook(block_num, block_size, total_size):
        if block_num // 2 == 0:
            return
        if total_size != -1:
            print(f"\rdownload_resource > {filename}文件大小：{total_size/1048576:.2f}MB | 下载进度：{block_num*block_size/total_size*100:.2f}%", end='')
        
    try:
        # create the object, assign it to a variable
        proxy_handler = request.ProxyHandler(proxies)
        # construct a new opener using your proxy settings
        opener = request.build_opener(proxy_handler)
        opener.addheaders = headers
        # install the openen on the module-level
        request.install_opener(opener)
        request.urlretrieve(url, filename, reporthook)
        print(f"\ndownload_resource > 文件已下载到：{filename}")
        return filename
    except Exception as e:
        print(f"\ndownload_resource > 下载文件时发生错误：{e}")
        raise e