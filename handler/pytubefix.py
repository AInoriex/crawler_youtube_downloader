from database.crawler_download_info import Video
from os import getenv, remove, path
from time import sleep, time
from handler.youtube_account import YoutubeAccout
from handler.youtube import get_youtube_vid
from utils.logger import logger
from utils.utime import get_now_time_string
from utils.lark import alarm_lark_text
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.helpers import reset_cache

_PROXIES = {'http': getenv("HTTP_PROXY"),'https': getenv("HTTP_PROXY")} if getenv("HTTP_PROXY", "") != "" else None

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

def init_pytubefix_client(youtube_url:str, proxies=_PROXIES, token_file:str=None)->YouTube:
    yt = YouTube(youtube_url, on_progress_callback=on_progress, proxies=proxies, allow_oauth_cache=True, use_oauth=True, token_file=token_file)
    if not yt:
        raise Exception(f"youtube url:{youtube_url} init pytubefix.YouTube failed")
    logger.debug(f"init_pytubefix_client > get {youtube_url} success")
    return yt

def pytubefix_audio_handler(yt:YouTube, video:Video, save_path:str, quality:str="best")->str|None:
    """
    pytubefix 下载音频
    :param video: Video instance
    :param save_path: save path of the downloaded audio
    :param quality: the quality of audio, default is "best"
    :return: str|None the path of the downloaded audio, None if failed
    :raises ValueError: if failed to download the audio
    :raises Exception: if failed to get audio stream by get_by_itag
    """
    if not video.source_link:
        logger.error(f"pytubefix_audio_handler > video source link is empty")
        return None

    # yt = YouTube(video.source_link, on_progress_callback=on_progress, proxies=_PROXIES, allow_oauth_cache=True, use_oauth=True)
    # yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies, use_oauth=True, token_file=r"cache\pytubefix_token\tokens.json")
    # logger.info(f"pytubefix_audio_handler > get the video {yt.title} from {yt.channel_url}")

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
    download_path = ys.download(output_path=save_path, filename=filename, skip_existing=True, max_retries=3, timeout=30)
    if not download_path:
        raise ValueError(f"pytubefix_audio_handler > download the video {video.source_link} fail")
    logger.debug(f"pytubefix_audio_handler > 音频已下载到:{download_path}")
    return download_path

def pytubefix_raw_video_handler(yt:YouTube, video:Video, save_path:str, quality:str="best")->str|None:
    """
    pytubefix 下载视频
    :param video: Video instance
    :param save_path: save path of the downloaded video
    :param quality: the quality of video, default is "best"
    :return: str|None the path of the downloaded video, None if failed
    :raises ValueError: if failed to download the video
    :raises Exception: if failed to get video stream by get_by_itag
    """
    if not video.source_link:
        logger.error(f"pytubefix_raw_video_handler > video source link is empty")
        return None

    # yt = YouTube(video.source_link, on_progress_callback=on_progress, proxies=_PROXIES, use_oauth=True, allow_oauth_cache=True)
    # yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies, use_oauth=True, token_file=r"cache\pytubefix_token\tokens.json")
    # logger.info(f"pytubefix_raw_video_handler > get the video {yt.title} from {yt.channel_url}")

    # 按照 itag 获取 video
    format_type = "mp4"
    
    # Itag details according to https://web.archive.org/web/20200516070826/https://gist.github.com/Marco01809/34d47c65b1d28829bb17c24c04a0096f
    # Default: 1080p > 720p > 480p > 360p > 240p > 144p
    # ::return:: <stream> | None
    ys = None
    # 1080p
    if yt.streams.get_by_itag(399):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 1080p AV1 HFR success")
        ys = yt.streams.get_by_itag(399)
    elif yt.streams.get_by_itag(248):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 1080p VP9 success")
        ys = yt.streams.get_by_itag(248) 
    elif yt.streams.get_by_itag(137):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 1080p H.264 success")
        ys = yt.streams.get_by_itag(137)
    # 720p
    elif yt.streams.get_by_itag(398):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 720p AV1 HFR success")
        ys = yt.streams.get_by_itag(398)
    elif yt.streams.get_by_itag(247):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 720p VP9 success")
        ys = yt.streams.get_by_itag(247) 
    elif yt.streams.get_by_itag(136):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 720p H.264 success")
        ys = yt.streams.get_by_itag(136)
    # 480p
    elif yt.streams.get_by_itag(397):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 480p AV1 success")
        ys = yt.streams.get_by_itag(397)
    elif yt.streams.get_by_itag(135):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 480p H.264 success")
        ys = yt.streams.get_by_itag(135)
    # 360p
    elif yt.streams.get_by_itag(396):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 360p AV1 success")
        ys = yt.streams.get_by_itag(396)
    elif yt.streams.get_by_itag(134):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 360p H.264 success")
        ys = yt.streams.get_by_itag(134)
    # 240p
    elif yt.streams.get_by_itag(395):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 240p AV1 success")
        ys = yt.streams.get_by_itag(395)
    elif yt.streams.get_by_itag(133):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 240p H.264 success")
        ys = yt.streams.get_by_itag(133)
    # 144p
    elif yt.streams.get_by_itag(394):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 144p AV1 success")
        ys = yt.streams.get_by_itag(394)
    elif yt.streams.get_by_itag(160):
        logger.debug(f"pytubefix_raw_video_handler > {video.vid} get 144p H.264 success")
        ys = yt.streams.get_by_itag(160)
    # couldn't match video itages
    else:
        raise Exception("pytubefix_raw_video_handler > get raw video stream by get_by_itag fail")
    
    # download_filepath = ys.download(output_path="download", filename_prefix="test-", skip_existing=True, max_retries=3, timeout=10)
    filename=f"{video.vid}.video.{format_type}"
    download_path = ys.download(output_path=save_path, filename=filename, skip_existing=True, max_retries=3, timeout=30)
    if not download_path:
        raise ValueError(f"pytubefix_raw_video_handler > download the video {video.source_link} fail")
    logger.debug(f"pytubefix_raw_video_handler > 视频已下载到:{download_path}")
    return download_path

def pytubefix_video_handler(video:Video, save_path:str, quality:str="best")->str|None:
    from utils.ffmpeg import merge_video_with_audio
    youtube_id = get_youtube_vid(video.source_link)
    dst_file = path.join(save_path, f"{youtube_id}.mp4")
    if path.exists(dst_file):
        logger.warning(f"pytubefix_video_handler > {dst_file} exists, skip download.")
        return dst_file
    yt = init_pytubefix_client(video.source_link)
    video_path = pytubefix_raw_video_handler(yt, video, save_path, quality)
    audio_path = pytubefix_audio_handler(yt, video, save_path, quality)
    return merge_video_with_audio(video_path, audio_path, dst_file)

def reset_pytubefix_oauth_token():
    # 清理旧token
    # reset_cache()

    # 初始化新token
    test_url = "https://www.youtube.com/watch?v=GFyAjmqpbCI"
    yt = YouTube(test_url, use_oauth=True, allow_oauth_cache=True, proxies=_PROXIES)
    ys = yt.streams.get_lowest_resolution()
    tmp_file = ys.download(output_path=".", filename="tmp_GFyAjmqpbCI.mp4", max_retries=3, timeout=10)
    remove(tmp_file)
    logger.debug("reset_pytubefix_oauth_token > 初始化新token完毕")