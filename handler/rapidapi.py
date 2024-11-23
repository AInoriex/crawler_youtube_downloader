import requests
from time import sleep
from random import choice, randint
from pprint import pprint
from loguru import logger
from os import getenv
from requests import HTTPError

proxies={
    'http': getenv("HTTP_PROXY") if getenv("HTTP_PROXY") != "" else "",
    'https': getenv("HTTP_PROXY") if getenv("HTTP_PROXY") != "" else "",
}

# 第三方解析youtube视频地址ytjar免费版
#  资源     360p mp4           
#  Refer    https://rapidapi.com/ytjar/api/ytstream-download-youtube-videos
#  Pricing  https://rapidapi.com/ytjar/api/youtube-video-download-info/pricing
#  Quota    500,000 / Month
#  QpsLimit 1000 requests per hour

ytjar_key_list = [
    "cc0f530252mshcd81b9c614428aep140232jsn4cb1d6dfebb3",
    "56921e587amshc0bb152f60c8571p1779d8jsn0c949090f93b",
    "8e4125bc5bmsheb83bbaba0c87a6p1dd95bjsn65084ee21b78"
]

def extract_download_url_ytjar_step1(video_id):
    url = "https://youtube-video-download-info.p.rapidapi.com/dl"
    querystring = {"id": video_id}
    headers = {
        "x-rapidapi-key": choice(ytjar_key_list),
        "x-rapidapi-host": "youtube-video-download-info.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring, proxies=proxies)
    response.raise_for_status()
    if response.status_code != 200:
        logger.error(f"extract_download_url_ytjar_step1 request {url} error, status:{response.status_code}")
        raise HTTPError(f"request {url} error", response=response)
    logger.debug(f"extract_download_url_ytjar_step1 response json {response.json()}")
    logger.info("extract_download_url_ytjar_step1 success")
    return response.json()

def extract_download_url_ytjar_step2(_middle_dict):
    import urllib.parse
    import re
    def _0xe14c(d, e, f):
        g = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
        h = g[:e]  # 源进制字符集
        i = g[:f]  # 目标进制字符集
        # 将源进制字符串转换为十进制
        j = 0
        for c, b in enumerate(d[::-1]):
            if b in h:
                j += h.index(b) * (e ** c)
        # 十进制转换为目标进制
        k = ""
        while j > 0:
            k = i[j % f] + k
            j //= f
        return k or "0"
    def decode_string(encoded_string, key1, key2, key3):
        r = ""
        i = 0
        n = key1  # 替代 n
        e = key3  # 替代 e
        t = key2  # 替代 t
        # 遍历编码字符串
        while i < len(encoded_string):
            s = ""
            # 提取子字符串直到遇到分隔符
            while i < len(encoded_string) and encoded_string[i] != n[e]:
                s += encoded_string[i]
                i += 1
            # 替换字符为数字
            for j in range(len(n)):
                s = s.replace(n[j], str(j))
            # 使用 _0xe14c 解码
            r += chr(int(_0xe14c(s, e, 10)) - t)
            i += 1  # 跳过分隔符
        # 最后解码字符串
        return urllib.parse.unquote(r)
    def parse_html(html_content):
        # 1. 提取 <script> 标签内的内容
        script_content = re.findall(r'<script>(.*?)</script><script>', html_content, re.DOTALL)
        # 如果提取到 <script> 标签内容
        if script_content:
            # 获取第一个 <script> 标签内容（如果有多个，可以用循环处理）
            script_content = script_content[0]
            # 2. 提取目标字符串部分
            pattern = r'\("([^"]+)",(\d+),"([^"]+)",(\d+),(\d+),(\d+)\)'
            match = re.search(pattern, script_content)
            if match:
                # 提取匹配到的元组内容
                return (match.group(1), int(match.group(2)), match.group(3), int(match.group(4)), int(match.group(5)),
                        int(match.group(6)))
            else:
                raise ValueError("No matching pattern found in the script content.")
        else:
            raise ValueError("No <script> content found in the provided HTML.")
    def parse_ts_th(text):
        ts_match = re.search(r'var tS = "([^"]+)";', text)
        th_match = re.search(r'var tH = "([^"]+)";', text)
        if ts_match and th_match:
            tS = ts_match.group(1)
            tH = th_match.group(1)
            return tS, tH
        else:
            raise ValueError("tS or tH not found in the input text.")

    # link_url = _middle_dict.get("link", {}).get("17", [""])[0] # 144p NOT SUPPORT
    # link_url = _middle_dict.get("link", {}).get("22", [""])[0] # 720p NOT SUPPORT
    link_url = _middle_dict.get("link", {}).get("18", [""])[0] # 360p
    if not link_url:
        raise ValueError("extract_download_url_ytjar_step2 extract empty link_url")
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        # 'cookie': '_gid=GA1.2.1474390812.1732154341; _ga=GA1.1.2108734893.1732152366; _ga_7HKSCJ4WQH=GS1.1.1732154340.1.1.1732154451.0.0.0; _ga_5C2KJN1R85=GS1.1.1732172790.4.1.1732172810.0.0.0',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    }
    # response = requests.get(link_url, headers=headers)
    response = requests.get(link_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    if response.status_code != 200:
        logger.error(f"extract_download_url_ytjar_step2 request {link_url} error, status:{response.status_code}")
        raise HTTPError(f"request {link_url} error", response=response)
    Encrypted_list = parse_html(response.text)
    logger.debug(f"extract_download_url_ytjar_step2 Encrypted_list: {Encrypted_list}")
    encoded_string = Encrypted_list[0]
    key1 = Encrypted_list[2]
    key2 = Encrypted_list[3]
    key3 = Encrypted_list[4]
    decoded_string = decode_string(encoded_string, key1, key2, key3)
    logger.debug(f"extract_download_url_ytjar_step2 decoded_string: {decoded_string}")
    logger.info("extract_download_url_ytjar_step2 success")
    return parse_ts_th(decoded_string)

def extract_download_url_ytjar_step3(video_id, tS, tH, retry=5):
    try:
        url = "https://mp4api.ytjar.info/get.v2.php"
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            # 'cookie': '_gid=GA1.2.1474390812.1732154341; _ga=GA1.1.2108734893.1732152366; _ga_7HKSCJ4WQH=GS1.1.1732154340.1.1.1732154451.0.0.0; _ga_5C2KJN1R85=GS1.1.1732172790.4.1.1732172810.0.0.0',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://mp4api.ytjar.info/dl2.php?id=GkFeNGqoW2B1iWVBfqAjTPDDlUjas8cYUflDQX8%3D&itag=17',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
        }
        params = {
            'id': video_id,
            's': tS,
            'h': tH,
        }
        # response = requests.get(url, params=params, headers=headers)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        response.raise_for_status()
        if response.status_code != 200:
            logger.error(f"extract_download_url_ytjar_step3 request {url} error, status:{response.status_code}")
            raise HTTPError(f"request {url} error", response=response)
        logger.debug(f"extract_download_url_ytjar_step3 response json {response.json()}")
        url = response.json().get("link", {}).get("18", [""])[0]
        logger.info(f"extract_download_url_ytjar_step3 success, url:{url}")
        if url == "":
            raise HTTPError("extract_download_url_ytjar_step3 failed, url is empty", response=response)
        return url
    except Exception as e:
        logger.error(f"extract_download_url_ytjar_step3 error, {e}, retry:{retry}")
        if retry > 0: # 防止接口处理中 {'status': 'fail', 'code': '403', 'processing': True, 'msg': 'Retry'}
            sleep(randint(1, 3))
            return extract_download_url_ytjar_step3(video_id=video_id, tS=tS, tH=tH, retry=retry-1)
        else:
            raise e

def extract_download_url_ytjar(video_id, retry=getenv("YTB_MAX_RETRY", 5))->str:
    """
    Extract download url from radpidapi of ytjar api.

    Args:
        video_id (str): The video id to extract download url.
        retry (int, optional): The retry count if the request failed. Defaults to 3.

    Raises:
        Exception: If the request failed.

    Returns:
        str: The specific download url of the video (exp. rr3---sn-i5heen7s.googlevideo.com/videoplayback?xxx).
    """
    try:
        middle_dict=extract_download_url_ytjar_step1(video_id)
        _tS, _tH=extract_download_url_ytjar_step2(middle_dict)
        video_url=extract_download_url_ytjar_step3(video_id, _tS, _tH)
        return video_url
    except Exception as e:
        logger.error(f"extract_download_url_ytjar error, {e}, retry:{retry}")
        if retry > 0:
            sleep(randint(1, 3))
            return extract_download_url_ytjar(video_id=video_id, retry=retry-1)
        else:
            raise e

if __name__ == "__main__":
    logger.add("logs/debug/ytjar.log", level="DEBUG")
    # logger.add("logs/debug/ytjar.log", level="INFO")
    result = extract_download_url_ytjar(video_id="HGrWeL8fHlU")
    pprint(result)