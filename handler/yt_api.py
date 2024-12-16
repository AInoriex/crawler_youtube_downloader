import requests
from requests import HTTPError
from time import sleep
from random import choice, randint
from os import getenv, path, remove
# from loguru import logger
from utils.logger import logger

proxies={
    'http': getenv("HTTP_PROXY") if getenv("HTTP_PROXY") != "" else "",
    'https': getenv("HTTP_PROXY") if getenv("HTTP_PROXY") != "" else "",
}

#  第三方解析youtube视频地址yt-api
#  资源     bestvideo+bestaudio  
#  Refer    https://rapidapi.com/ytjar/api/yt-api
#  Pricing  https://rapidapi.com/ytjar/api/yt-api/pricing
#  Quota    500 / Day
#  QpsLimit 1000 requests per hour

ytapi_key_list = [
    # "cc0f530252mshcd81b9c614428aep140232jsn4cb1d6dfebb3",
    # "56921e587amshc0bb152f60c8571p1779d8jsn0c949090f93b",
    "8e4125bc5bmsheb83bbaba0c87a6p1dd95bjsn65084ee21b78"
]

def ytapi_handler_step1(vid:str, cgeo:str="RU")->dict:
    url = "https://yt-api.p.rapidapi.com/dl"
    querystring = {
        "id": vid,
        "cgeo": cgeo,
    }
    headers = {
        "x-rapidapi-key": choice(ytapi_key_list),
        "x-rapidapi-host": "yt-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring, proxies=proxies)
    response.raise_for_status()
    if response.status_code != 200:
        logger.error(f"ytapi_handler_step1 request {url} error, status:{response.status_code}")
        raise HTTPError(f"request {url} error", response=response)
    logger.debug(f"ytapi_handler_step1 response json {response.json()}")
    logger.info(f"ytapi_handler_step1 success, vid:{vid}")
    return response.json()

def ytapi_handler_step2(json_data:dict)->tuple[str, str]:
    """ 解析响应提取下载链接 """
    qualityLabel_list = ["1080p", "720p", "480p", "360p"]
    audioQuality_list = ["AUDIO_QUALITY_MEDIUM", "AUDIO_QUALITY_LOW", "AUDIO_QUALITY_ULTRALOW"]
    video_url, audio_url = "", ""
    formats = json_data.get("adaptiveFormats", [])
    for qualityLabel in qualityLabel_list:
        for fmt in formats:
            if qualityLabel == fmt.get("qualityLabel", "") and fmt.get("url", "") != "":
                logger.debug(f"ytapi_handler_step2 video hit:{qualityLabel}")
                video_url = fmt.get("url", "")
        if video_url:
            break
    for audioQuality in audioQuality_list:
        for fmt in formats:
            if audioQuality == fmt.get("audioQuality", "") and fmt.get("url", "") != "":
                logger.debug(f"ytapi_handler_step2 audio hit:{audioQuality}")
                audio_url = fmt.get("url", "")
        if audio_url:
            break
    logger.info(f"ytapi_handler_step2 success, \nvideo_url:{video_url}, \naudio_url:{audio_url}")
    return video_url, audio_url

def ytapi_download(url:str, filename:str, retry=3)->str:
    if url == "" or filename == "":
        raise ValueError("ytapi_download url or filename is empty")
    from handler.tubedown import download_resource
    try:
        download_path = download_resource(url, filename)
        return download_path
    except Exception as e:
        logger.error(f"ytapi_download error, url:{url}, filename:{filename}, error:{e}, retry:{retry}")
        if retry > 0:
            sleep(randint(1, 3))
            return ytapi_download(url=url, filename=filename, retry=retry-1)
        else:
            raise e

def ytapi_handler_step3(video_url:str, audio_url:str, save_path:str)->tuple[str, str]:
    """ 下载视频 """
    from uuid import uuid4
    from handler.tubedown import get_mime_type
    if video_url == "" or audio_url == "":
        raise ValueError(f"ytapi_handler_step3 params invalid, video_url:{video_url}, audio_url:{audio_url}")
    video_path, audio_path = "", ""
    try:
        logger.debug(f"ytapi_handler_step3 start download video url: {video_url}")
        video_path = ytapi_download(
            url = video_url,
            filename = path.join(save_path, f"{uuid4()}.video.{get_mime_type(video_url, default='mp4')}"),
        )
        logger.debug(f"ytapi_handler_step3 start download audio url: {audio_url}")
        audio_path = ytapi_download(
            url = audio_url, 
            filename = path.join(save_path, f"{uuid4()}.audio.{get_mime_type(audio_url, default='mp4')}"),
        )
        logger.info(f"ytapi_handler_step3 download success, video_path:{video_path}, audio_path:{audio_path}")
        return video_path, audio_path
    except Exception as e:
        if video_path != "" and path.exists(video_path):
            remove(video_path)
        if audio_path != "" and path.exists(audio_path):
            remove(audio_path)
        raise e

def ytapi_handler_step4(video_path:str, audio_path:str, dst_path:str)->str:
    """ 合并视频和音频 """
    import subprocess
    from uuid import uuid4
    if video_path == "" or audio_path == "":
        raise ValueError(f"ytapi_handler_step4 params invalid, video_path:{video_path}, audio_path:{audio_path}")
    # 构建ffmpeg命令
    command = [
        'ffmpeg',
        '-i', video_path,  # 输入的视频文件
        '-i', audio_path,  # 输入的音频文件
        '-c:v', 'copy',    # 复制视频流
        '-c:a', 'aac',     # 使用AAC编码音频流
        '-strict', 'experimental',  # 某些版本的ffmpeg需要这个参数来启用aac编码
        '-y', dst_path  # 输出文件路径
    ]

    # 调用ffmpeg命令
    try:
        subprocess.run(command, check=True)
        logger.info(f"ytapi_handler_step4 ffmpeg merge success, dst_path:{dst_path}")
        return dst_path
    except subprocess.CalledProcessError as e:
        logger.error(f"ytapi_handler_step4 error, {video_path} + {audio_path} => {dst_path}, error:{e}")
        raise e

def ytapi_handler(video_id:str, save_path:str, cgeo:str="US", retry:int=3)->str:
    """
    Extract download url from radpidapi of yt-api.

    Args:
        video_id (str): The video id to extract download url.
        cgeo (str): Country code in ISO 3166 format of the end user, default US.
        retry (int, optional): The retry count if the request failed. Defaults to 3.

    Raises:
        Exception: If the request failed.

    Returns:
        str: The specific download url of the video (exp. rr3---sn-i5heen7s.googlevideo.com/videoplayback?xxx).
    """
    try:
        response = ytapi_handler_step1(video_id, cgeo)
        video_url, audio_url = ytapi_handler_step2(response)
        video_path, audio_path = ytapi_handler_step3(video_url, audio_url, save_path)
        dst_path = path.join(save_path, f"{video_id}.mp4")
        dst_path = ytapi_handler_step4(video_path, audio_path, dst_path)
        remove(video_path)
        remove(audio_path)
        return dst_path
    except Exception as e:
        logger.error(f"ytapi_handler error:{e}, retry:{retry}")
        if retry > 0:
            sleep(randint(1, 3))
            return ytapi_handler(video_id=video_id, save_path=save_path, cgeo=cgeo,retry=retry-1)
        else:
            raise e
