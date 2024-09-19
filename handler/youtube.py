from os import path, makedirs, walk, getenv
from handler.info import dump_info
from utils.utime import random_sleep
import yt_dlp
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
import pytz

def make_path(save_path):
    ''' 预创建下载目录 '''
    # |—— audio
    # |—— info
    save_audio_path = path.join(save_path, "audio")
    save_info_path = path.join(save_path, "info")
    makedirs(save_audio_path, exist_ok=True)
    makedirs(save_info_path, exist_ok=True)
    return save_audio_path, save_info_path

# 下载单个视频或者播放列表
def download_url(url, save_path):
    if "watch" in url:
        return download_by_watch_url(url, save_path)
    else:
        return download_by_playlist_url(url, save_path)

def load_options(save_audio_path:str):
    ''' 配置yt_dlp下载模式 '''
    # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    # See details at https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py
    DEBUG_MODE = getenv("YTB_DEBUG", False) == "True"
    OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
    if OAUTH2_PATH:
        print(f"Yt-dlp+oauth2 > load cache in {OAUTH2_PATH}")
    else:
        print(f"Yt-dlp+oauth2 > use default cache")

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
        
        # 下载文件格式配置
        # # 提取视频
        "outtmpl": save_audio_path + "/%(id)s.%(ext)s",
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
       
        # 账号鉴权
        "username": "oauth2",
        "password": "",
        "cachedir": OAUTH2_PATH, # Location of the cache files in the filesystem. False to disable filesystem cache.
    }

def generate_video_info(vid, ydl:YoutubeDL):
    ''' 生成视频信息（yt_dlp只获取信息不下载） '''
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

def download_by_watch_url(video_url, save_path, retry=int(getenv("YTB_MAX_RETRY"))):
    ''' 下载油管单个视频 https://www.youtube.com/watch?v=xxx '''
    print(f"Yt-dlp > download_by_watch_url参数 video_url:{video_url} save_path:{save_path} retry:{retry}")
    __vid = ""
    try:
        save_audio_path, save_info_path = make_path(save_path)
        ydl_opts = load_options(save_audio_path)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = generate_video_info(video_url, ydl)
            __vid = info_dict["id"]
            save_to_json_file = f"{save_info_path}/{__vid}.json"
            ydl.download(__vid)
            dump_info(info_dict, save_to_json_file)
            print(f"Yt-dlp > download_by_watch_url生成下载信息：{save_to_json_file}")
    except Exception as e:
        if retry > 0:
            if "Video unavailable" in e.msg: # 账号不可使用
                print(f"Yt-dlp > [!] 账号可能无法使用，请换号重试")
                retry = 1
            retry = retry - 1
            random_sleep(rand_st=5, rand_range=5)
            return download_by_watch_url(video_url, save_path, retry=retry)
        else:
            if __vid != "":
                save_to_fail_file = f"{save_info_path}/{__vid}.fail.json"
                dump_info(info_dict, save_to_fail_file)
            raise e
    else:
        return try_to_get_file_name(save_audio_path, __vid, path.join(save_audio_path, f"{__vid}.mp4"))

def download_by_playlist_url(playlist_url:str, save_path:str, ydl_opts={}, max_limit=0, retry=int(getenv("YTB_MAX_RETRY")), fail_limit=int(getenv("YTB_FAIL_COUNT"))):
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
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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

def format_into_watch_url(url:str):
    '''
    @Desc   格式化链接保留参数v
    @Params url:https://www.youtube.com/watch?v=6s416NmSFmw&list=PLRMEKqidcRnAGC6j1oYPFV9E26gyWdgU4&index=4
    @Return 6s416NmSFmw, https://www.youtube.com/watch?v=6s416NmSFmw
    '''
    vid = str("")
    try:
        # 解析URL
        parsed_url = urlparse(url)
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        if len(query_params) > 1:
            # 保留查询参数中的v
            if 'v' in query_params:
                vid = query_params['v'][0]
                new_query_params = {'v': vid}
            else:
                raise ValueError
            
            # 构建新的查询字符串
            new_query_string = urlencode(new_query_params, doseq=True)
            
            # 构建新的URL
            new_url = urlunparse(parsed_url._replace(query=new_query_string))
        else:
            if 'v' in query_params:
                vid = str(query_params['v'][0])
                new_url = url
            else:
                raise ValueError
    except Exception as e:
        print(f"Yt-dlp > format_into_watch_url failed, url:{url}, error:{e.__str__}")
        return vid, ""
    else:
        # print(f"format_into_watch_url succeed, url:{url}")
        return vid, new_url;

def try_to_get_file_name(save_dir:str, vid:str, default_name='')->str:
    ''' 尝试获取下载文件名 '''
    ret_name = ""
    # files = []
    for dirpath, dirnames, filenames in walk(save_dir):
        for filename in filenames:
            # files.append(path.join(dirpath, filename))
            if ".part" in filename:
                print("try_to_get_file_name > part文件跳过获取")
                continue
            if vid in filename:
                ret_name = (path.join(dirpath, filename))
                break
    if ret_name == "":
        ret_name = default_name
    print(f"try_to_get_file_name > 获取到本地资源文件{ret_name}")
    return ret_name

def is_touch_fish_time()->bool:
    ''' 判断是否能摸鱼，以Youtube总部地区为限制 '''
    ytb_timezone = "America/Los_Angeles"

    # 获取当前时间
    now_utc = datetime.now(pytz.utc)
    
    # 转换为美国加利福尼亚州时区时间
    pacific_tz = pytz.timezone(ytb_timezone)
    now_pacific = now_utc.astimezone(pacific_tz)
    
    # 获取当前的小时
    current_hour = now_pacific.hour
    current_mint = now_pacific.minute
    
    # 判断是否在办公时间内(早上9点到下午5点)
    if 9 <= current_hour < 17+1:
        print(f"[×] 非摸鱼时间 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return False
    else:
        print(f"[√] 摸鱼时间 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return True

def get_ytb_playlist_title(playlist_url:str, ydl_opts={}):
    '''
    @Desc     获取播放列表标题
    @Return   info['title'] | empty string
    '''
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False, process=False)
        # print(f"Info: {info}")
        title = info.get("title", "")
        print(f"get_ytb_playlist_title > Playlist Title: {title}")
    return title