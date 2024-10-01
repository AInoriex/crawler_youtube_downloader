from pytz import utc, timezone
from os import path, makedirs, walk, getenv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
from database.youtube_api import Video
from handler.yt_dlp import download_by_watch_url, download_by_playlist_url

def download_url(url, save_path):
    ''' 下载油管单个视频或者播放列表 '''
    if "watch" in url:
        return download_by_watch_url(url, save_path)
    else:
        return download_by_playlist_url(url, save_path)

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
    now_utc = datetime.now(utc)
    
    # 转换为美国加利福尼亚州时区时间
    pacific_tz = timezone(ytb_timezone)
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

def get_cloud_save_path_by_language(save_path:str, lang_key:str)->str:
    ''' 获取云存储路径
    @Paras  src_path: /DATA/{LANGUAGE}/youtube/ db_lang: vt
    @Return /DATA/Vietnam/youtube/
    '''
    ret_path = str("")   
    LANGUAGE_PATH_DICT = {
        "vi": "Vietnam", # 越南语
        "yue": "Yueyu", # 粤语
        "nan": "Minnanyu", # 闽南语
        "th": "Taiyu", # 泰语
        "id": "Yinniyu", # 印尼语
        "ms": "Malaiyu", # 马来语
        "fil": "Feilvbinyu", # 菲律宾语
        "en": "English", # 英语
        "zh": "Zhongwen", # 中文
        "unknown": "Unclassify" # 未知
    }
    if "{LANGUAGE}" in save_path:
        ret_path = save_path.format(LANGUAGE=LANGUAGE_PATH_DICT.get(lang_key, "Unclassify"))
    else:
        ret_path = save_path
    return ret_path