from database.crawler_download_info import Video
from handler.youtube_accout import YoutubeAccout
from os import getenv, remove
from time import sleep, time
from utils.logger import logger
from utils.utime import get_now_time_string
from utils.lark import alarm_lark_text
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.helpers import reset_cache

def pytubefix_login_handler()->YoutubeAccout:
    """
    登录pytubefix
    1. 获取可用账号
    2. 登录账号获取token
    3. token保存到文件
    4. 更新状态

    :return: YoutubeAccout
    """
    try:
        # 1. 获取可用账号
        account = YoutubeAccout()
        account.get_new_account()
        if account.id <= 0 or account.username == "" or account.password == "" or account.verify_email == "":
            raise Exception("pytubefix_login_handler 获取新账号失败")

        # 2. 登录账号获取token
        print("pytubefix_login_handler > 正在自动登陆账号中，请稍后...")
        token = account.account_auto_login(
            url=getenv("CRAWLER_AUTO_LOGIN_API"),
            username=account.username,
            password=account.password,
            verify_email=account.verify_email,
        )
        # token = {"yt-dlp_version":"2024.07.16","data":{"access_token":"ya29.a0ARW5m77x_oaR27kwgMoLkuilpbie_BiF92PXUWK6XJeB44yQjWjfBwnLWsTBeGcGz5A8q_vgdwUfSU51bm-X0lQYsxqx3I9Xv5cBBqfZcgsMs4JtP7k6ENBRrzcLPLQA5PWtHiSx0IE27eFAW56h8zUDnChidg_xFZxSdRAJuIhCB1q-2aHjaCgYKATUSARESFQHGX2MifKbYwHaU_fsIhaoN6Eddbg0187","expires":1736248157.389038,"refresh_token":"1//0ggz4_-Msif4SCgYIARAAGBASNwF-L9IrFTNepc7Qp2lMEKHdKavzEcjDeCAqyBy-OfxNR_pd5wYPAc3tZ3hzBKU7_a4ojuauLVw","token_type":"Bearer"}}
        if not token:
            raise Exception("pytubefix_login_handler 自动登陆账号失败, token为空")

        # 封装pytubefix token格式
        account.token = token["data"]
        account.token["visitorData"] = None
        account.token["po_token"] = None

        # 3. token保存到文件
        token_path = account.save_token_to_file(
            token=account.token,
            save_dir=f"./cache/pytubefix_{int(time())}"
        )
        if token_path == "":
            raise Exception("pytubefix_login_handler 保存token失败")
        account.token_path = token_path

        # 4. 更新状态
        account.login(is_login=True)
    except Exception as e:
        logger.error(f"pytubefix_login_handler > unknown error:{e}")
        notice_text = f"[Youtube Crawler ACCOUNT | ERROR] 自动换号失败. \
            \n\t登入方: {account.login_name} \
            \n\t账密: {account.id} | {account.username} {account.password} \
            \n\tERROR: {e} \
            \n\t告警时间: {get_now_time_string()}"
        alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
        if account.id > 0:
            account.login(is_login=False)
        raise e
    else:
        notice_text = f"[Youtube Crawler ACCOUNT | INFO] 自动换号成功. \
            \n\t登入方: {account.login_name} \
            \n\t账密: {account.id} | {account.username} {account.password} \
            \n\tToken Path: {account.token_path} \
            \n\tToken Content: {account.token} \
            \n\t告警时间: {get_now_time_string()}"
        alarm_lark_text(webhook=getenv("LARK_INFO_WEBHOOK"), text=notice_text)

def pytubefix_audio_handler(video:Video, save_path:str)->str|None:
    """
    pytubefix 下载音频
    :param video: Video instance
    :param save_path: save path of the downloaded video
    :return: str|None the path of the downloaded video, None if failed
    :raises ValueError: if failed to download the video
    :raises Exception: if failed to get audio stream by get_by_itag
    """
    if not video.source_link:
        logger.error(f"pytubefix_audio_handler > video source link is empty")
        return None
    proxies = {'http': getenv("HTTP_PROXY"),'https': getenv("HTTP_PROXY")} if getenv("HTTP_PROXY", "") != "" else None

    yt = YouTube(video.source_link, on_progress_callback=on_progress, proxies=proxies, allow_oauth_cache=True, use_oauth=True)
    # yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies, use_oauth=True, token_file=r"cache\pytubefix_token\tokens.json")
    logger.info(f"pytubefix_audio_handler > get the video {yt.title} from {yt.channel_url}")

    # 按照 itag 获取 audio
    format_type = "mp3"
    
    # Itag details according to https://web.archive.org/web/20200516070826/https://gist.github.com/Marco01809/34d47c65b1d28829bb17c24c04a0096f
    # ::return:: <stream> | None
    ys = None
    if yt.streams.get_by_itag(251):
        logger.debug("pytubefix_audio_handler > get WebM.Opus ~160 Kbps success")
        format_type = "opus"
        ys = yt.streams.get_by_itag(251)
    elif yt.streams.get_by_itag(250):
        logger.debug("pytubefix_audio_handler > get WebM.Opus ~70 Kbps success")
        format_type = "opus"
        ys = yt.streams.get_by_itag(250) 
    elif yt.streams.get_by_itag(249):
        logger.debug("pytubefix_audio_handler > get WebM.Opus ~50 Kbps success")
        format_type = "opus"
        ys = yt.streams.get_by_itag(249) 
    elif yt.streams.get_by_itag(140):
        logger.debug("pytubefix_audio_handler > get MP4.AAC 128 Kbps success")
        format_type = "m4a"
        ys = yt.streams.get_by_itag(140) 
    else:
        raise Exception("pytubefix_audio_handler > get audio stream by get_by_itag fail")
    
    # download_filepath = ys.download(output_path="download", filename_prefix="test-", skip_existing=True, max_retries=3, timeout=10)
    filename=f"{video.vid}.{format_type}"
    download_path = ys.download(output_path=save_path, filename=filename, skip_existing=True, max_retries=3, timeout=10)
    if not download_path:
        raise ValueError(f"pytubefix_audio_handler > download the video {video.source_link} fail")
    logger.debug(f"pytubefix_audio_handler > 文件已下载到:{download_path}")
    return download_path

def reset_pytubefix_oauth_token():
    # 清理旧token
    reset_cache()

    # 初始化新token
    test_url = "https://www.youtube.com/watch?v=GFyAjmqpbCI"
    yt = YouTube(test_url, use_oauth=True, allow_oauth_cache=True)
    ys = yt.streams.get_lowest_resolution()
    tmp_file = ys.download(output_path=".", filename="tmp_GFyAjmqpbCI.mp4", max_retries=3, timeout=10)
    remove(tmp_file)