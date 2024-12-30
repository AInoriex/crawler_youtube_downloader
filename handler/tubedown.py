# https://tubedown.cn/youtube
from time import sleep, time
from os import getenv
import requests
from random import choice, randint
# from loguru import logger
from utils.logger import logger

def get_random_ua():
    from fake_useragent import UserAgent
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

def extract_download_url(youtube_url, retry=3):
    ua = get_random_ua()
    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://tubedown.cn',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://tubedown.cn/youtube',
        'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-ch-ua-platform': ua.get('os'),
        'user-agent': ua.get('ua'),
        # 'sec-ch-ua-platform': '"Windows"',
        # 'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }

    json_data = {
        'url': youtube_url,
    }
    try:
        response = requests.post('https://tubedown.cn/api/youtube', headers=headers, json=json_data, timeout=12)
        if response.status_code != 200:
            raise AssertionError(f"tubedown request failed, {response.status_code} | {str(response.content, encoding='utf-8')}")

        video_info = {}
        audio_info = {}
        audio_info_list = []
        highest_tbr = 0
        json_data = response.json()
        response_code = json_data.get("code", -1)
        if response_code != 0:
            raise ValueError(f"tubedown request failed, {response_code} | {json_data.get('message', 'unknown error')}")

        # 解析data数据
        formats = json_data.get("data", {}).get("formats", [])
        for resolution in ["(1080p)", "(720p)", "(480p)", "(360p)", "(240p)", "(144p)"]:
            for fmt in formats:
                if resolution in fmt.get('format', "") and fmt.get('protocol', "") == "https":
                    tbr_value = int(fmt.get("tbr", 0))
                    if tbr_value > highest_tbr:
                        video_info = fmt
                        highest_tbr = tbr_value
            if video_info:
                break

        for fmt in formats:
            if fmt.get('protocol', "") == "https" and "audio only" in fmt.get('format', ""):
                audio_info_list.append(fmt)  # 收集所有音频格式
        for audio_quality in ["medium, DRC", "medium", "low, DRC", "low"]:
            for audio_fmt in audio_info_list:
                if audio_quality in audio_fmt.get("format", ""):
                    audio_info = audio_fmt
                    break
            if audio_info:
                break

        if not video_info:
        # if not (video_info or audio_info):
            raise ValueError("extract_download_url get empty data info")
    except Exception as e:
        logger.error(f"Error occurred while processing formats: {e}", exc_info=True)
        if retry > 0:
            sleep(randint(2,5))
            extract_download_url(youtube_url=youtube_url, retry=retry-1)
        else:
            raise e
    else:
        return {"video_info": video_info, "audio_info": audio_info}

def download_resource(url:str, filename:str, proxies={}):
    """
    使用代理服务器从url处下载文件到本地的filename

    :param url: 要下载的文件的url
    :param filename: 保存到本地的文件名
    :return: None
    """
    import urllib.request as request
    print(f"download_file > 参数：{url} -- {filename}")
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
            print(f"\r文件大小：{total_size/1048576:.2f}MB | 下载进度：{block_num*block_size/total_size*100:.2f}%", end='')
        
    try:
        # create the object, assign it to a variable
        if proxies:
            proxy_handler = request.ProxyHandler(proxies)
        else:
            proxy_handler = request.ProxyHandler()

        # construct a new opener using your proxy settings
        opener = request.build_opener(proxy_handler)
        opener.addheaders = headers

        # install the openen on the module-level
        request.install_opener(opener)

        request.urlretrieve(url, filename, reporthook)
    except Exception as e:
        print(f"\ndownload_file > 下载文件时发生错误：{e}")
        raise e
    else:
        print(f"\ndownload_file > 文件已下载到：{filename}")
        return filename

def get_youtube_vid(url:str):
    import re
    from uuid import uuid4
    default = uuid4()
    try:
        # 使用正则表达式匹配v参数
        video_id_match = re.search(r"v=([^&#]+)", url)
        if video_id_match:
            video_id = video_id_match.group(1)
            return video_id
        else:
            raise ValueError("get_youtube_vid re.search failed")
    except Exception as e:
        logger.error(f"get_youtube_vid > error, {e}")
        return default
    
def get_mime_type(url, default="mp4"):
    import re
    try:
        mime_match = re.search(r"mime=([^&]+)", url)
        if mime_match:
            mime_value = mime_match.group(1)
            return mime_value.split("%2F")[1]
        else:
            raise ValueError("get_mime_type re.search failed")
    except Exception as e:
        logger.error(f"get_mime_type > error, {e}")
        return default

if __name__ == '__main__':
    st = time()
    url = 'https://www.youtube.com/watch?v=6gk91dpHNo8'
    try:
        down_info = extract_download_url(url)
    except Exception as e:
        print(e)
    else:
        video_url = down_info.get("video_info", {}).get("url")
        audio_url = down_info.get("audio_info", {}).get("url")
        logger.info(f"视频下载地址：{video_url}")
        logger.info(f"音频下载地址：{audio_url}")
        logger.info(f"用时：{round(time()-st, 2)} seconds")

    # video_url = """https://rr5---sn-i3belnl6.googlevideo.com/videoplayback?expire=1730743103&ei=37YoZ-7pE6mL1d8PpuSSoAg&ip=206.237.16.169&id=o-AMqSU8CgVxIH7TiXp-ejgwYjc5egEGRri94MHuP6JL5a&itag=137&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1730721503%2C&mh=J1&mm=31%2C29&mn=sn-i3belnl6%2Csn-i3b7knlk&ms=au%2Crdu&mv=u&mvi=5&pl=23&rms=au%2Cau&vprv=1&svpuc=1&mime=video%2Fmp4&rqh=1&gir=yes&clen=111254201&dur=952.117&lmt=1722468130058420&mt=1730720796&fvip=5&keepalive=yes&fexp=51312688%2C51326932&c=IOS&txp=5532434&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cvprv%2Csvpuc%2Cmime%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAI2AeKv9gk8J0nwA8hVeQWqX_2Eb2T6jn9IlXkZG-RGPAiEAjQuNKvxz2EQxFyn-hGc1UhIh1pDDDmMT_HcJM96dM9k%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms&lsig=ACJ0pHgwRQIhAPB6DzETifN5V5xom8i4C4xYUZisYzVtRy40IiwvejNlAiBJLYvDAudGcsmbbysV_kpNEbfAmf8I5LxP6rISGfcDBw%3D%3D"""
    # get_url_resource(video_url, r"./download/test.mp4")
    download_resource(video_url, r"./download/test.mp4")
