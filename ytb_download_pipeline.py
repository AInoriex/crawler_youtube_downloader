# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import json
from os import getenv, path, remove
from time import time, sleep
from urllib.parse import urljoin
from traceback import format_exc
from handler.youtube import is_touch_fish_time, get_cloud_save_path_by_language, get_youtube_vid
from handler.yt_dlp import clean_path
from database.youtube_api import get_video_for_download, update_video_record
from utils.logger import logger
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.file import get_file_size
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
from database.crawler_download_info import Video
# from handler.youtube_accout import YoutubeAccout
# from handler.bilibili import download as bilibili_download
# from handler.ximalaya import download as ximalaya_download

# ---------------------
# ---- 初始化参数 -----
# ---------------------

LOCAL_IP = get_local_ip()
''' 本地IP '''
SERVER_NAME = getenv("SERVER_NAME")
''' 服务名称 '''
LIMIT_FAIL_COUNT = int(getenv("LIMIT_FAIL_COUNT"))
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(getenv("LIMIT_LAST_COUNT"))
''' 连续处理任务限制数 '''
CLOUD_TYPE = "obs" if getenv("OBS_ON", False) == "True" else "cos"
''' 云端存储类别，上传cos或者obs '''
if CLOUD_TYPE == "obs":
    # from utils.obs import upload_file as obs_upload_file
    from utils.obs import upload_file_v2 as obs_upload_file_v2
elif CLOUD_TYPE == "cos":
    from utils.cos import upload_file as cos_upload_file
else:
    raise ValueError("")
DOWNLOAD_PATH = getenv('DOWNLOAD_PATH')
''' YouTube资源下载目录'''
# OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
''' YouTube账号缓存目录'''
print("[INFO] > 配置项初始化完毕")

# ---------------------------------------------------------------

def youtube_sleep(is_succ:bool, run_count:int, download_round:int):
    """
    任务处理 sleep 机制

    :param is_succ: bool, 任务是否处理成功
    :param run_count: int, 任务处理次数
    :param download_round: int, 任务处理轮数

    1. 触发轮数限制,每轮固定等2mins
    2. 任务处理成功
        2.1.摸鱼时间,间隔10s以上
        2.2.非摸鱼时间,间隔20s以上
    3. 任务处理失败
        3.1.摸鱼时间,等待30s以上
        3.2.非摸鱼时间,等待1min以上
    """
    now_round = run_count//LIMIT_LAST_COUNT + 1
    if now_round > download_round:
        print(f"[INFO] > 触发轮数限制, 当前轮数：{now_round}")
        random_sleep(rand_st=60, rand_range=30)
        return
    if is_succ:
        if is_touch_fish_time():
            random_sleep(rand_st=10, rand_range=10)
        else:
            random_sleep(rand_st=20, rand_range=10)
    else:
        if is_touch_fish_time():
            random_sleep(rand_st=30, rand_range=20)
        else:
            random_sleep(rand_st=60, rand_range=20)

def download_with_yt_dlp(video:Video, save_path:str):
    from handler.yt_dlp import download_by_watch_url
    download_path = download_by_watch_url(video, save_path=save_path)
    if download_path == "":
        raise("download_with_yt_dlp download_path empty")
    return download_path

def download_with_tubedown(video:Video, save_path:str):
    from handler.tubedown import tubedown_handler
    download_path = tubedown_handler(video, save_path)
    if download_path == "":
        raise ValueError("download_with_tubedown get empty download file")
    return download_path

def download_with_rapidapi(video:Video, save_path:str):
    from handler.youtube import get_youtube_vid, get_mime_type
    from utils.request import download_resource
    # 1 解析真实视频url
    from handler.rapidapi import extract_download_url_ytjar
    dst_url = extract_download_url_ytjar(video_id=get_youtube_vid(video.source_link))

    # 2 合并音视频资源(根据实际接口返回结果判断)
    # TODO

    # 3 下载视频资源
    filename = path.join(save_path, f"{get_youtube_vid(video.source_link)}.{get_mime_type(dst_url, default='mp4')}")
    download_path = download_resource(
        url = dst_url, 
        filename = filename, 
        proxies = {'http': getenv("HTTP_PROXY"),'https': getenv("HTTP_PROXY")} if getenv("HTTP_PROXY", "") != "" else {}
    )
    if download_path == "":
        raise ValueError("download_with_rapidapi get empty download file")
    return download_path

def download_with_yt_api(video:Video, save_path:str):
    from handler.yt_api import ytapi_handler
    download_path = ytapi_handler(
        video_id=get_youtube_vid(video.source_link),
        save_path=save_path
    )
    if download_path == "":
        raise ValueError("download_with_yt_api get empty download file")
    return download_path

def download_with_pytubefix_audio(video:Video, save_path:str):
    from handler.pytubefix import pytubefix_audio_handler
    download_path = pytubefix_audio_handler(video, save_path)
    if not download_path:
        raise ValueError("download_with_pytubefix_audio get empty download file")
    return download_path

def download_with_pytubefix_video(video:Video, save_path:str):
    from handler.pytubefix import pytubefix_video_handler
    download_path = pytubefix_video_handler(video, save_path)
    download_path = ""
    if not download_path:
        raise ValueError("download_with_pytubefix_video get empty download file")
    return download_path

def youtube_download_handler(video:Video, save_path):
    if getenv("YTB_DOWNLOAD_MODE", "") == "tubedown":
        logger.info("youtube_download_handler > 当前下载模式: tubedown")
        return download_with_tubedown(video, save_path)
    elif getenv("YTB_DOWNLOAD_MODE", "") == "rapidapi":
        logger.info("youtube_download_handler > 当前下载模式: rapidapi")
        return download_with_rapidapi(video, save_path)
    elif getenv("YTB_DOWNLOAD_MODE", "") == "yt_api":
        logger.info("youtube_download_handler > 当前下载模式: yt_api")
        return download_with_yt_api(video, save_path)
    elif getenv("YTB_DOWNLOAD_MODE", "") == "yt_dlp":
        logger.info("youtube_download_handler > 当前下载模式: yt_dlp")
        return download_with_yt_dlp(video, save_path)
    elif getenv("YTB_DOWNLOAD_MODE", "") == "pytubefix_audio":
        logger.info("youtube_download_handler > 当前下载模式: pytubefix_audio")
        return download_with_pytubefix_audio(video, save_path)
    elif getenv("YTB_DOWNLOAD_MODE", "") == "pytubefix_video":
        logger.info("youtube_download_handler > 当前下载模式: pytubefix_video")
        return download_with_pytubefix_video(video, save_path)
    else:
        logger.warning("youtube_download_handler > 未配置下载模式, 默认: yt_dlp")
        return download_with_yt_dlp(video, save_path)

def main_pipeline(pid):
    sleep(15 * pid)
    logger.debug(f"Pipeline > 进程 {pid} 开始执行")

    download_round = int(1)      # 当前下载轮数
    run_count = int(0)           # 持续处理的任务个数l
    continue_fail_count = int(0) # 连续失败的任务个数
    while True:
        video = get_video_for_download(
            query_source_type=int(getenv("DOWNLOAD_SOURCE_TYPE")),
            query_language=getenv("DOWNLOAD_LANGUAGE"),
        )
        if video is None:
            logger.warning(f"Pipeline > 当前轮次: {download_round} | {run_count}, 进程 {pid} 无任务待处理, 等待中...")
            random_sleep(rand_st=20, rand_range=10)
            continue
        if video.id <= 0 or video.source_link == "":
            logger.warning(f"Pipeline > 当前轮次: {download_round} | {run_count}, 进程 {pid} 获取无效任务, 跳过处理...")
            random_sleep(rand_st=20, rand_range=10)
            continue
        try:
            run_count += 1
            video_id = video.id
            video_link = video.source_link
            logger.info(f"Pipeline > 当前轮次: {download_round} | {run_count}, 进程 {pid} 处理任务 {video_id} -- {video_link}")
            if video.info not in [None, "", "{}"]:
                info = json.loads(video.info)
                cloud_save_path = info.get("cloud_save_path", "")
            else:
                cloud_save_path = ""

            # 下载
            time_1 = time()
            download_path = youtube_download_handler(video, DOWNLOAD_PATH)
            spend_download_time = max(time() - time_1, 0.01) #下载花费时间
            logger.success(f"Pipeline > 进程 {pid} 处理任务 {video_id} 下载完成, from: {video_link}, to: {download_path}")
            
            # 上传云端
            time_2 = time()
            cloud_path = urljoin(
                get_cloud_save_path_by_language(
                    save_path=cloud_save_path if cloud_save_path !='' else getenv("CLOUD_SAVE_PATH"),
                    lang_key=video.language
                ), 
                path.basename(download_path)
            )
            logger.info(f"Pipeline > 进程 {pid} 处理任务 {video_id} 准备上传 `{CLOUD_TYPE}`, from: {download_path}, to: {cloud_path}")
            if CLOUD_TYPE == "obs":
                cloud_link = obs_upload_file_v2(
                    from_path=download_path, to_path=cloud_path
                )
            elif CLOUD_TYPE == "cos":
                cloud_link = cos_upload_file(
                    from_path=download_path, to_path=cloud_path
                )
            else:
                raise ValueError("invalid cloud type")
            spend_upload_time = max(time() - time_2, 0.01) #上传花费时间
            logger.success(f"Pipeline > 进程 {pid} 处理任务 {video_id} 上传完成, from: {download_path}, to: {cloud_link}")
            
            # 更新数据库
            video.status = 2 # 2:已上传云端
            video.cloud_type = 2 if CLOUD_TYPE == "obs" else 1 # 1:cos 2:obs
            video.cloud_path = cloud_link
            update_video_record(video)
            logger.success(f"Pipeline > 进程 {pid} 处理任务 {video_id} 更新数据库完成")
            
            # 日志记录
            spend_total_time = int(time() - time_1) #总花费时间
            file_size = get_file_size(download_path)
            logger.info(
                f"Pipeline > 进程 {pid} 完成处理任务 {video_id}, 已上传至 {cloud_path}, 文件大小: {file_size} MB, 共处理了 {format_second_to_time_string(spend_total_time)}"
            )
            
            # 移除本地文件
            remove(download_path)
            logger.success(f"Pipeline > 进程 {pid} 移除本地文件 {download_path}")

            # 通知
            notice_text = f"[Youtube Crawler] download pipeline success. \
                \n\t下载服务: {SERVER_NAME} | 进程: {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count} \
                \n\t资源信息: {video.id} | {video.vid} | {video.language} \
                \n\tLink: {video.source_link} -> {video.cloud_path} \
                \n\t资源共 {file_size:.2f}MB , 共处理了{format_second_to_time_string(spend_total_time)} \
                \n\t下载时长: {format_second_to_time_string(spend_download_time)} , 上传时长: {format_second_to_time_string(spend_upload_time)} \
                \n\t下载均速: {file_size/spend_download_time:.2f}M/s , 上传均速: {file_size/spend_upload_time:.2f}M/s \
                \n\tIP: {LOCAL_IP} | {get_public_ip()}"
            logger.info(notice_text)
            alarm_lark_text(webhook=getenv("LARK_INFO_WEBHOOK"), text=notice_text)

            logger.success(f"Pipeline > 进程 {pid} 处理任务 {video_id} 完毕")
        except KeyboardInterrupt:
            logger.warning(f"Pipeline > 进程 {pid} interrupted processing {video_id}, reverting...")
            # 任务回调
            video.lock = 0
            update_video_record(video)
            raise KeyboardInterrupt
        # except BrokenPipeError as e: # 账号被封处理
        #     return
        except Exception as e:
            continue_fail_count += 1
            time_fail = time()
            logger.error(f"Pipeline > 进程 {pid} 处理任务 {video_id} 失败, 错误信息:{e}")
            # 任务回调
            video.status = -1
            video.lock = 0
            video.comment += f'<div class="download_pipeline">pipeline error:{e}, error_time:{get_now_time_string()}</div>'
            update_video_record(video)
            # 告警
            notice_text = f"[Youtube Crawler | ERROR] download pipeline failed. \
                \n\t下载服务: {SERVER_NAME} | {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count}\
                \n\t资源信息: {video.id} | {video.vid} | {video.language} \
                \n\tSource Link: {video.source_link} \
                \n\t共处理了{format_second_to_time_string(int(time_fail-time_1))} \
                \n\tIP: {LOCAL_IP} | {get_public_ip()} \
                \n\tError: {e} \
                \n\t告警时间: {get_now_time_string()} \
                \n\tStack Info: {format_exc()[-500:]}"
            logger.error(notice_text)
            alarm_lark_text(webhook=getenv("LARK_INFO_WEBHOOK"), text=notice_text)
            # 失败过多直接退出
            if continue_fail_count > LIMIT_FAIL_COUNT:
                logger.error(f"Pipeline > 进程 {pid} 失败过多超过{continue_fail_count}次, 异常退出")
                alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
                # 退出登陆
                # if getenv("CRAWLER_SWITCH_ACCOUNT_ON", False) == "True":
                #     ac.logout(is_invalid=True, comment=f"{SERVER_NAME}失败过多退出, {e}")
                return
            youtube_sleep(is_succ=False, run_count=run_count, download_round=download_round)
            continue
        else:
            continue_fail_count = 0
            youtube_sleep(is_succ=True, run_count=run_count, download_round=download_round)
        finally:
            download_round = run_count//LIMIT_LAST_COUNT + 1

if __name__ == "__main__":
    # 清理旧目录文件
    clean_path(DOWNLOAD_PATH)

    # 初始化 pytubefix token
    if getenv("YTB_DOWNLOAD_MODE", "").startswith("pytubefix"):
        from handler.pytubefix import reset_pytubefix_oauth_token
        reset_pytubefix_oauth_token()

    import multiprocessing
    # PROCESS_NUM = 1 #同时处理的进程数量
    PROCESS_NUM = int(getenv("PROCESS_NUM"))
    try:
        with multiprocessing.Pool(PROCESS_NUM) as pool:
            for i in range(PROCESS_NUM):
                pool.apply_async(main_pipeline, (i,))
            pool.close()
            pool.join()
        # main_pipeline(0)
    except Exception as e:
        logger.critical(f"[ERROR] > Exception raise: {e.__class__} | {e}")
        pool.terminate()
    finally:
        pass