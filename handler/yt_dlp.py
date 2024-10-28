import traceback
from os import path, makedirs, getenv, removedirs
from shutil import rmtree
from handler.info import dump_info
from yt_dlp import YoutubeDL
from database.youtube_api import Video
from utils.utime import random_sleep

def make_path(save_path):
    ''' 预创建下载目录 '''
    # save_path
    #   |—— resource
    #   └── info
    save_audio_path = path.join(save_path, "resource")
    save_info_path = path.join(save_path, "info")
    makedirs(save_audio_path, exist_ok=True)
    makedirs(save_info_path, exist_ok=True)
    return save_audio_path, save_info_path

def clean_path(save_path):
    ''' 清理下载目录 '''
    if path.exists(save_path):
        rmtree(save_path)
        print("Yt-dlp > 已清理旧目录及文件: ", save_path)
    save_audio_path = path.join(save_path, "resource")
    save_info_path = path.join(save_path, "info")
    makedirs(save_audio_path, exist_ok=True)
    makedirs(save_info_path, exist_ok=True)
    print("Yt-dlp > 已初始化目录: ", save_path)
    pass

def yt_dlp_init(v:Video, save_path:str, video_ext:str="mp4", audio_ext:str="m4a", subtitle_ext:str="srt")->dict:
    save_media_path, save_info_path = make_path(save_path)

    ''' 配置yt_dlp下载模式 '''
     # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    # See details at https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
    DEBUG_MODE = getenv("DEBUG", False) == "True"
    if getenv("CRAWLER_SWITCH_ACCOUNT_ON", False) == "True":
        from handler.youtube_accout import OAUTH2_PATH
    else:
        OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
    if OAUTH2_PATH:
        print(f"Yt-dlp+oauth2 > load cache in {OAUTH2_PATH}")
    else:
        print(f"Yt-dlp+oauth2 > use default cache")

    return {
        # Self Options
        "save_media_path": save_media_path,
        "save_info_path": save_info_path,

        # 下载配置
        "quiet": False if DEBUG_MODE else True, # Do not print messages to stdout.
        "verbose": True if DEBUG_MODE else False, # Print additional info to stdout.
        "proxy": (
            getenv("HTTP_PROXY")
            if getenv("HTTP_PROXY") != ""
            else None
        ),
        "ratelimit": 10 * 1024 * 1024, # x * M,
        "nooverwrites": True,
        "continuedl": True, # Continue download
        "noplaylist": True, # 不下载列表所有视频
        # "playlistreverse": True,
        "sleep_interval": 2,
        # "paths": save_media_path + "/",
        "outtmpl": save_media_path + "/%(id)s.%(ext)s",
        
        # 下载格式配置
        # # 提取视频
        # "format": f"bestvideo[ext={video_ext}]+bestaudio[ext={audio_ext}]/best[ext={video_ext}]/best",
        "format": f"bestvideo[height<=1080]+bestaudio/bestvideo[filesize<=3000M]+bestaudio/bestvideo+bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": video_ext,  # one of avi, flv, mkv, mp4, ogg, webm
        }],

        # # 提取音频
        # "format": "m4a/bestaudio/best",
        # "postprocessors": [
        #     {  # Extract audio using ffmpeg
        #         "key": "FFmpegExtractAudio",
        #         "preferredcodec": "m4a",
        #     }
        # ],

        # 提取字幕
        # "skip_download": True,
        # "writesubtitles": True, # 是否提取字幕
        # "subtitleslangs": ["en"], # 提取的语言
        # "subtitleslangs": [v.language],
        # "subtitlesformat": f"all/{subtitle_ext}",
        # "subtitlesformat": f"srt",
        # "subtitle": "--write-srt --sub-lang en",
        # "listsubtitles": True,
        # "writeautomaticsub": True, # 自动生成vtt
        # "postprocessors": [{
        #     "key": "FFmpegSubtitlesConvertor",
        #     "format": subtitle_ext,
        # }],
        
        # 账号鉴权
        "username": "oauth2",
        "password": "",
        "cachedir": OAUTH2_PATH, # Location of the cache files in the filesystem. False to disable filesystem cache.
    }

def load_options(local_save_path:str):
    ''' 配置yt_dlp下载模式 '''
    # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    # See details at https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
    DEBUG_MODE = getenv("DEBUG", False) == "True"
    OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
    if OAUTH2_PATH:
        print(f"Yt-dlp > OAuth2 load cache in {OAUTH2_PATH}")
    else:
        print(f"Yt-dlp > OAuth2 use default cache")

    return {
        # 下载配置
        "quiet": False if DEBUG_MODE else True, # Do not print messages to stdout.
        "verbose": True if DEBUG_MODE else False, # Print additional info to stdout.
        "dumpjson": True,
        "proxy": (
            getenv("HTTP_PROXY")
            if getenv("HTTP_PROXY") != ""
            else None
        ),
        "ratelimit": 5 * 1024 * 1024, # x * M,
        "nooverwrites": True,
        "continuedl": True, # Continue download
        # "playlistreverse": True,
        "sleep_interval": 1,
        "paths": local_save_path,
        
        # 下载文件格式配置
        # # 提取视频
        "outtmpl": local_save_path + "/%(id)s.%(ext)s",
        # "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",  # one of avi, flv, mkv, mp4, ogg, webm
        }],

        # # 提取音频
        # "format": "m4a/bestaudio/best",
        # "postprocessors": [
        #     {  # Extract audio using ffmpeg
        #         "key": "FFmpegExtractAudio",
        #         "preferredcodec": "m4a",
        #     }
        # ],

        # 提取字幕
        # "writesubtitles": True,
        # "subtitleslangs": "ar",
        # "subtitlesformat": "srt",
        
        # 账号鉴权
        "username": "oauth2",
        "password": "",
        "cachedir": OAUTH2_PATH, # Location of the cache files in the filesystem. False to disable filesystem cache.
    }

def download_video_info(vid, ydl:YoutubeDL):
    ''' yt-dlp 提取视频信息 '''
    video_info = ydl.extract_info(vid, download=False, process=False)

    info_dict = {
        "id": video_info["id"],
        # "title": video_info["title"],
        # "full_url": video_info["webpage_url"],
        # "author": video_info["uploader_id"],
        # "duration": video_info["duration"],
        # "categories": video_info["categories"],
        # "tags": video_info["tags"],
        # "view_count": video_info["view_count"],
        # "comment_count": video_info["comment_count"],
        # "follower_count": video_info["channel_follower_count"],
        # "upload_date": video_info["upload_date"],
    }
    return info_dict

def get_ytb_playlist_title(playlist_url:str, ydl_opts={}):
    '''
    @Desc     获取播放列表标题
    @Return   info['title'] | empty string
    '''
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False, process=False)
        # print(f"Info: {info}")
        title = info.get("title", "")
        print(f"get_ytb_playlist_title > Playlist Title: {title}")
    return title

# def download_by_watch_url(watch_url, save_path=getenv("DOWNLOAD_PATH"), retry=int(getenv("YTB_MAX_RETRY"))):
def download_by_watch_url(v:Video, save_path:str, retry=int(getenv("YTB_MAX_RETRY"))):
    ''' 下载油管单个视频 https://www.youtube.com/watch?v=xxx '''
    if retry <= 0:
        raise Exception(f"Yt-dlp > download_by_watch_url retry failed")
    print(f"\nYt-dlp > download_by_watch_url参数 video_url:{v.source_link} language:{v.language}, save_path:{save_path} retry:{retry}")
    __vid = ""
    try:
        # save_media_path, save_info_path = make_path(save_path)
        # ydl_opts = load_options(save_media_path)
        ydl_opts = yt_dlp_init(
            v,
            save_path,
            video_ext="mp4",
            audio_ext="m4a",
            subtitle_ext="srt",
        )
        with YoutubeDL(ydl_opts) as ydl:
            # 下载资源信息
            info_dict = download_video_info(v.source_link, ydl)
            __vid = info_dict["id"]
            # info_filename = path.join(ydl_opts["save_info_path"], f"{__vid}.json")
            # dump_info(info_dict, info_filename)
            # print(f"Yt-dlp > download_by_watch_url 生成下载信息: {info_filename}")

            # 下载资源
            ydl.download(__vid)
            media_filename = path.join(ydl_opts["save_media_path"], f"{__vid}.mp4")
            print(f"Yt-dlp > download_by_watch_url 资源下载完成: {media_filename}")

            # 下载字幕
            # if ydl_opts["writesubtitles"]:
            #     subtitle_filename = path.join(ydl_opts["save_media_path"], f"{__vid}.srt")
            #     ydl.process_subtitles(__vid, subtitle_filename)
            #     print(f"Yt-dlp > download_by_watch_url 字幕下载完成: {subtitle_filename}")

    except Exception as e:
        print("Yt-dlp > [!] download_by_watch_url 处理失败", traceback.format_exception)
        if retry > 0:
            # 账号失效1: Video unavailable
            if 'msg' in e.__dict__ and "Video unavailable" in e.msg: 
                print(f"Yt-dlp > [!] 账号可能无法使用，请换号重试, {e.msg}")
                raise BrokenPipeError(f"账号失效, {e.msg}")
            # 账号失效2: Sign in to confirm you’re not a bot. This helps protect our community. Learn more
            elif 'msg' in e.__dict__ and "Sign in" in e.msg:
                print(f"Yt-dlp > [!] 账号可能无法使用，请换号重试, {e.msg}")
                raise BrokenPipeError(f"账号失效, {e.msg}")
            random_sleep(rand_st=1, rand_range=4)
            return download_by_watch_url(v, save_path, retry=retry-1)
        else:
            if __vid != "":
                save_to_fail_file = path.join(ydl_opts["save_info_path"], f"{__vid}.fail.json")
                dump_info(info_dict, save_to_fail_file)
            raise e
    else:
        return media_filename

def download_by_playlist_url(playlist_url:str, save_path:str, ydl_opts={}, max_limit=0, retry=int(getenv("YTB_MAX_RETRY")), fail_limit=int(getenv("LIMIT_FAIL_COUNT"))):
    ''' 下载油管播放列表playlist到本地 https://www.youtube.com/playlist?list=xxx '''
    # 手动获取playlist title
    playlist_title = get_ytb_playlist_title(playlist_url)  # 获取播放列表标题
    save_path = path.join(save_path, playlist_title)  # 创建以播放列表标题命名的目录
    print(f"download_by_playlist_v2 > 保存目录在:{save_path}")
    makedirs(save_path, exist_ok=True)  # 确保目录存在
    # 使用yt-dlp识别playlist title
    # ydl_opts["outtmpl"] = path.join(save_path, "%(id)s.%(ext)s")
    # save_path = path.join(save_path, "%(playlist)s", "%(playlist_index)s-%(title)s.%(ext)s")
    
    if ydl_opts == {}:
        ydl_opts = load_options(save_path)
    success_count = 0
    fail_count = 0
    result_paths = []
    with YoutubeDL(ydl_opts) as ydl:
        author_info = ydl.extract_info(playlist_url, download=False, process=False)
        for entry in author_info["entries"]:
            if max_limit != 0 and success_count >= max_limit:
                print("download_by_playlist_url > YouTube触发下载条数限制:",
                    max_limit,
                    "video(s). Quitting.",
                )
                break
            vid = entry["id"]
            print(f"download_by_playlist_url > 当前视频链接： https://www.youtube.com/watch?v={vid}")
            while True:
                try:
                    ydl.download(vid)
                except Exception as e:
                    fail_count += 1
                    print(f"download_by_playlist_url > 下载视频失败 {e} | retry: {retry} | fail: {fail_count}")
                    if fail_count > fail_limit:
                        raise SystemError(f"download_by_playlist_url failed to much:{fail_count}, {e}")
                    continue
                else:
                    success_count += 1
                    fail_count = 0
                    name = path.join(save_path, f"{vid}.mp4")
                    result_paths.append(name)
                    print(f"download_by_playlist_url > 下载视频成功 {name}")
                    break
                finally:
                    retry -= 1
                    if retry <= 0:
                        print(f"download_by_playlist_url > 重试过多退出取消下载 https://www.youtube.com/watch?v={vid}")
                        break
                    random_sleep(rand_st=5, rand_range=5)
    print(f"download_by_playlist_url > 该列表下载完毕，成功: {success_count}条")
    return result_paths

def yt_dlp_subtitles_handler():
    ''' 处理下载字幕 '''
    import subprocess

    # 定义命令
    command = [
        "yt-dlp",
        "--skip-download",
        "--write-automatic-subs",
        "--convert-subs", "srt",
        "--sub-langs", "vi",
        "-o", "./srt/%(id)s.%(ext)s",
        "https://www.youtube.com/watch?v=rGUthJ7Ojso"
    ]

    # 执行命令
    try:
        subprocess.run(command, check=True)
        print("命令执行成功")
    except subprocess.CalledProcessError as e:
        print("命令执行失败:", e)
    return
