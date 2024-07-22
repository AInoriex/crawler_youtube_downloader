# from utils.tool import load_cfg
# cfg = load_cfg("config.json")
# from config import Config
# config = Config()
# config.load_cfg("conf/config.json")
# cfg = config.cfg

import yt_dlp
from yt_dlp import YoutubeDL
import time
import random
from handler.info import dump_info
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from os import path, makedirs, walk, getenv
MAX_RETRY = int(getenv("YTB_MAX_RETRY"))

# 预创建下载目录
# |—— audio
# |—— info
def make_path(save_path):
    save_audio_path = path.join(save_path, "audio")
    save_info_path = path.join(save_path, "info")
    makedirs(save_audio_path, exist_ok=True)
    makedirs(save_info_path, exist_ok=True)
    return save_audio_path, save_info_path

def yt_dlp_monitor(self, d):
    final_filename = d.get('info_dict').get('_filename')
    # You could also just assign `d` here to access it and see all the data or even `print(d)` as it updates frequently

# 配置yt_dlp下载模式
def load_options(save_audio_path):
    # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    return {
        "quiet": False,
        "dumpjson": True,
        "proxy": (
            # cfg["common"]["http_proxy"]
            getenv("HTTP_PROXY")
            if getenv("HTTP_PROXY") != ""
            else None
        ),
        "outtmpl": save_audio_path + "/%(id)s.%(ext)s",
        
        # 提取视频
        # "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "format": "bestvideo+bestaudio/best",
        # 提取音频
        # "format": "m4a/bestaudio/best",
        # "postprocessors": [
        #     {  # Extract audio using ffmpeg
        #         "key": "FFmpegExtractAudio",
        #         "preferredcodec": "m4a",
        #     }
        # ],
       
        "username": "oauth2",
        "password": "",
        "ratelimit": 100 * 1024 * 1024, # x * M,
        "verbose": True, # Useful for checking if we have the latest version.
        "nooverwrites": True,
        "continuedl": True,
        # "playlistreverse": True,
        # "restrictfilenames": True,
    }

# 生成视频信息（yt_dlp只获取信息不下载）
def generate_video_info(vid, ydl:YoutubeDL):
    video_info = ydl.extract_info(vid, download=False, process=False)

    info_dict = {
        "id": video_info["id"],
        "title": video_info["title"],
        "full_url": video_info["webpage_url"],
        "author": video_info["uploader_id"],
        "duration": video_info["duration"],
        "categories": video_info["categories"],
        "tags": video_info["tags"],
        "view_count": video_info["view_count"],
        "comment_count": video_info["comment_count"],
        "follower_count": video_info["channel_follower_count"],
        "upload_date": video_info["upload_date"],
    }
    return info_dict

# 下载单个视频或者播放列表
def download(url, save_path):
    if "watch" in url:
        return download_by_watch_url(url, save_path)
    else:
        return download_by_playlist(url, save_path)

# 下载普通油管链接(支持只有请求参数v)
# exp.  https://www.youtube.com/watch?v=6s416NmSFmw&list
def download_by_watch_url(video_url, save_path, __retry=MAX_RETRY):
    print(f"download_by_watch_url参数 video_url:{video_url} save_path:{save_path} retry:{__retry}")
    try:
        save_audio_path, save_info_path = make_path(save_path)
        ydl_opts = load_options(save_audio_path)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if __retry == MAX_RETRY:
                info_dict = generate_video_info(video_url, ydl)
                vid = info_dict["id"]
                save_to_json_file = f"{save_info_path}/{vid}.json"
                dump_info(info_dict, save_to_json_file)
                print(f"download_by_watch_url生成下载信息：{save_to_json_file}")

            ydl.download(vid)
    except Exception as e:
        if __retry > 0:
            __retry = __retry - 1
            return download_by_watch_url(video_url, save_path, __retry=__retry)
        else:
            raise e
    else:
        # return path.join(save_audio_path, f"{vid}.webm")
        return try_to_get_file_name(save_audio_path, vid, path.join(save_audio_path, f"{vid}.webm"))

# 下载油管播放列表链接
# exp.  
def download_by_playlist(playlist_url, save_path, max_limit=0):
    save_audio_path, save_info_path = make_path(save_path)

    success_num = 0
    ydl_opts = load_options(save_audio_path)
    result_paths = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        author_info = ydl.extract_info(playlist_url, download=False, process=False)

        for entry in author_info["entries"]:
            if success_num >= max_limit and max_limit != 0:
                print(
                    "> YouTube: Successfully downloaded",
                    max_limit,
                    "video(s). Quitting.",
                )
                break
            vid = entry["id"]
            info_dict = generate_video_info(vid, ydl)

            save_to_json_file = f"{save_info_path}/{vid}.json"
            try:
                ydl.download(vid)
                time.sleep(random.uniform(5, 10))  # sleep in case got banned by YouTube
                dump_info(info_dict, save_to_json_file)
                result_paths.append(path.join(save_audio_path, f"{vid}.webm"))
                success_num += 1
            except Exception as e:
                print("> YouTube: \033[31mEXCEPTION OCCURED.\033[0m")
                print(e)
                continue
    return result_paths

# 格式化链接保留参数v
# exp.  url:https://www.youtube.com/watch?v=6s416NmSFmw&list=PLRMEKqidcRnAGC6j1oYPFV9E26gyWdgU4&index=4
#       out: https://www.youtube.com/watch?v=6s416NmSFmw
def format_into_watch_url(url:str)->str:
    try:
        # 解析URL
        parsed_url = urlparse(url)
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        if len(query_params) > 1:
            # 保留查询参数中的v
            if 'v' in query_params:
                new_query_params = {'v': query_params['v']}
            else:
                raise ValueError
            
            # 构建新的查询字符串
            new_query_string = urlencode(new_query_params, doseq=True)
            
            # 构建新的URL
            new_url = urlunparse(parsed_url._replace(query=new_query_string))
        else:
            if 'v' in query_params:
                new_url = url
            else:
                raise ValueError
    except Exception as e:
        print(f"format_into_watch_url failed, url:{url}, error:{e.__str__}")
        return ""
    else:
        print(f"format_into_watch_url succeed, url:{url}")
        return new_url


def try_to_get_file_name(save_dir:str, vid:str, default_name='')->str:
    ''' 尝试获取下载文件名 '''
    ret_name = ""
    # files = []
    for dirpath, dirnames, filenames in walk(save_dir):
        for filename in filenames:
            # files.append(path.join(dirpath, filename))
            if vid in filename:
                ret_name = (path.join(dirpath, filename))
                break
    if ret_name == "":
        ret_name = default_name
    return ret_name