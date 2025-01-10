from time import sleep, time
from os import getenv, path, remove
import requests
from random import choice, randint
from database.crawler_download_info import Video
from handler.youtube import get_youtube_vid, get_mime_type
from utils.logger import logger
from utils.request import get_random_ua, download_resource
from utils.ffmpeg import merge_video_with_audio

# @Desc:    借助tubedown.cn处理youtube视频
# @Refer:   https://tubedown.cn/youtube
# @Limit:   仅限于国内访问
# @Update:  2025.01.11 11:01

_PROXIES = {'http': getenv("HTTP_PROXY"),'https': getenv("HTTP_PROXY")} if getenv("HTTP_PROXY", "") != "" else None

def request_tubedown_api(youtube_url:str)->requests.Response:
    try:
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
        response = requests.post('https://tubedown.cn/api/youtube', headers=headers, json=json_data, timeout=12)
        if response.status_code != 200:
            raise AssertionError(f"request_tubedown_api status_code not 200, {response.status_code} | {str(response.content, encoding='utf-8')}")
        json_data = response.json()
        response_code = json_data.get("code", -1)
        if response_code != 0:
            raise ValueError(f"request_tubedown_api request failed, {response_code} | {str(response.text(), encoding='utf-8')}")
        return response
    except Exception as e:
        logger.error(f"request_tubedown_api > error:{e}")
        raise e

def extract_video_url(response:requests.Response)->str:
    """
    根据tubedown.cn的API响应，提取视频下载地址url

    :param response: tubedown.cn的API响应
    :return: 视频下载地址url
    :raises ValueError: 如果解析结果为空
    """
    highest_tbr = 0 # 记录最高清晰度
    try:
        json_data = response.json()
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
        # 检查提取结果
        if not video_info:
            raise ValueError("extract_video_url get empty video info")
        video_url = video_info.get("url")
        if not video_url:
            raise ValueError("extract_video_url get empty video url")
        logger.debug(f"extract_video_url > video_url:{video_url}")
        return video_url
    except Exception as e:
        logger.error(f"extract_video_url > error:{e}")
        raise e

def extract_audio_url(response:requests.Response)->str:
    """
    根据tubedown.cn的API响应，提取音频频下载地址url

    :param response: tubedown.cn的API响应
    :return: 音频下载地址url
    :raises ValueError: 如果解析结果为空
    """
    audio_info_list = [] # 记录所有音频格式
    try:
        json_data = response.json()
        formats = json_data.get("data", {}).get("formats", [])
        for fmt in formats:
            if fmt.get('protocol', "") == "https" and "audio only" in fmt.get('format', ""):
                audio_info_list.append(fmt)
        for audio_quality in ["medium, DRC", "medium", "low, DRC", "low"]:
            for audio_fmt in audio_info_list:
                if audio_quality in audio_fmt.get("format", ""):
                    audio_info = audio_fmt
                    break
            if audio_info:
                break
        # 检查提取结果
        if not audio_info:
            raise ValueError("extract_audio_url get empty video info")
        audio_url = audio_info.get("url")
        if not audio_url:
            raise ValueError("extract_audio_url get empty video url")
        logger.debug(f"extract_audio_url > audio_url:{audio_url}")
        return audio_url
    except Exception as e:
        logger.error(f"extract_audio_url > error:{e}")
        raise e

def tubedown_handler(video:Video, save_path:str, retry:int=int(getenv("LIMIT_MAX_RETRY", 3)))->str:
    if video.source_link == "":
        raise ValueError("tubedown_handler get empty source link")
    try:
        # 请求API提取信息
        response = request_tubedown_api(video.source_link)
        youtube_vid = get_youtube_vid(video.source_link)

        # 下载视频资源
        video_url = extract_video_url(response)
        video_file = path.join(save_path, f"{youtube_vid}.video.{get_mime_type(video_url, default='mp4')}")
        if path.exists(video_file):
            logger.warning(f"tubedown_handler > video file already exists, skip download, video_file:{video_file}")
        else:
            video_file = download_resource(url=video_url, filename=video_file, proxies=_PROXIES)

        # 下载音频资源
        audio_url = extract_audio_url(response)
        # audio_file = path.join(save_path, f"{youtube_vid}.audio.{get_mime_type(video_url, default='mp3')}")
        audio_file = path.join(save_path, f"{youtube_vid}.audio.m4a")
        if path.exists(audio_file):
            logger.warning(f"tubedown_handler > audio file already exists, skip download, audio_file:{audio_file}")
        else:
            audio_file = download_resource(url=audio_url, filename=audio_file, proxies=_PROXIES)

        # 合并音视频资源
        # video_file = r"download\test\6gk91dpHNo8.video.mp4"
        # audio_file = r"download\test\6gk91dpHNo8.video.m4a"
        dst_filename = path.join(save_path, f"{youtube_vid}.mp4")
        dst_path = merge_video_with_audio(video_file, audio_file, dst_filename)

        # 清理临时文件
        remove(video_file)
        remove(audio_file)

        return dst_path
    except Exception as e:
        logger.error(f"tubedown_handler > error:{e}, retry:{retry}")
        if retry > 0:
            sleep(randint(1, 3))
            return tubedown_handler(video=video, save_path=save_path, retry=retry-1)
        else:
            raise e
