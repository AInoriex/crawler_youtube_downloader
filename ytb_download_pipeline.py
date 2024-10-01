# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import json
from os import getenv, walk, path, remove
from time import time, sleep
from urllib.parse import urljoin
from handler.youtube import is_touch_fish_time, download_by_watch_url, get_cloud_save_path_by_language
# from handler.bilibili import download as bilibili_download
# from handler.ximalaya import download as ximalaya_download
from database.youtube_api import get_video_for_download, update_video_record
from utils import logger
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.file import get_file_size
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
from utils.cos import upload_file as cos_upload_file
from utils.obs import upload_file as obs_upload_file

# ---------------------
# ---- 初始化参数 -----
# ---------------------

logger = logger.init_logger("main_download")
local_ip = get_local_ip()

SERVER_NAME = getenv("SERVER_NAME")
''' 处理失败任务限制数 '''
LIMIT_FAIL_COUNT = int(getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''
CLOUD_TYPE = "obs" if getenv("OBS_ON", False) == "True" else "cos"
''' 云端存储类别，上传cos或者obs '''
SOURCE_TYPE = int(getenv("DOWNLOAD_SOURCE_TYPE"))
''' 下载来源 '''

# ---------------------

def youtube_sleep(is_succ:bool, run_count:int, download_round:int):
    """ 油管下载间隔等待规则 """
    now_round = run_count//LIMIT_LAST_COUNT + 1
    if now_round > download_round:
        logger.info(f"Pipeline > 触发轮数限制, 当前轮数：{now_round}")
        random_sleep(rand_st=60*2, rand_range=1) #每轮固定等2mins
        return

    if is_succ:
        if is_touch_fish_time():
            random_sleep(rand_st=5, rand_range=10) #处理成功间隔5s以上
        else:
            random_sleep(rand_st=10, rand_range=10) #处理成功间隔10s以上(非摸鱼时间)
    else:
        if is_touch_fish_time():
            random_sleep(rand_st=30, rand_range=30) #请求失败等待0.5mins以上
        else:
            random_sleep(rand_st=60, rand_range=30) #请求失败等待1mins以上(非摸鱼时间)

def main_pipeline(pid):
    sleep(30 * pid)
    logger.debug(f"Pipeline > pid {pid} started")
    download_round = int(1)      # 当前下载轮数
    run_count = int(0)           # 持续处理的任务个数
    continue_fail_count = int(0) # 连续失败的任务个数

    while True:
        # video = get_video_for_download(query_id=0, query_source_type=SOURCE_TYPE)
        video = get_video_for_download(query_id=668925)

        if video is None:
            logger.info(f"Pipeline > pid {pid} no task which has processed {run_count} tasks, waiting...")
            random_sleep(rand_st=20, rand_range=10)
            continue
        id = video.id
        link = video.source_link
        info = json.loads(video.info)
        cloud_save_path = info.get("cloud_save_path", "")

        try:
            run_count += 1
            logger.info(f"Pipeline > pid {pid} processing {id} -- {link}, 轮数 {download_round} | 处理数 {run_count}")
            time_1 = time()

            # 下载(本地存在不会被覆盖，续传)
            download_path = download_by_watch_url(v=video, save_path=getenv('DOWNLOAD_PATH'))
            time_2 = time()
            spend_download_time = max(time_2 - time_1, 0.01) #下载花费时间
            
            # 上传云端
            cloud_path = urljoin(
                get_cloud_save_path_by_language(
                    save_path=cloud_save_path if cloud_save_path !='' else getenv("CLOUD_SAVE_PATH"),
                    lang_key=video.language
                ), 
                path.basename(download_path)
            )
            logger.info(f"Pipeline > pid {pid} processing {id} is ready to upload, from: {download_path}, to: {cloud_path}")
            if CLOUD_TYPE == "obs":
                # cloud_path = urljoin(getenv("OBS_SAVEPATH"), path.basename(download_path))
                cloud_link = obs_upload_file(
                    from_path=download_path, to_path=cloud_path
                )
            elif CLOUD_TYPE == "cos":
                # cloud_path = urljoin(getenv("COS_SAVEPATH"), path.basename(download_path))
                cloud_link = cos_upload_file(
                    from_path=download_path, to_path=cloud_path
                )
            else:
                raise ValueError("invalid cloud type")
            time_3 = time()
            spend_upload_time = max(time_3 - time_2, 0.01) #上传花费时间
            
            # 更新数据库
            video.status = 2 # upload done
            video.cloud_type = 2 if CLOUD_TYPE == "obs" else 1 # 1:cos 2:obs
            video.cloud_path = cloud_link
            update_video_record(video)
            
            # 日志记录
            spend_total_time = int(time_3 - time_1) #总花费时间
            file_size = get_file_size(download_path)
            logger.info(
                f"Pipeline > pid {pid} done processing {id}, uploaded to {cloud_path}, \
                    file_size: {file_size} MB, spend_time: {format_second_to_time_string(spend_total_time)} seconds"
            )
            
            # 移除本地文件
            remove(download_path)

        except KeyboardInterrupt:
            logger.warning(f"Pipeline > pid {pid} interrupted processing {id}, reverting...")
            # revert lock to 0
            video.lock = 0
            update_video_record(video)
            break
        except Exception as e:
            continue_fail_count += 1
            time_fail = time()
            logger.error(f"Pipeline > pid {pid} error processing {id}")
            logger.error(e, stack_info=True)
            # 任务回调
            video.status = -1
            video.lock = 0
            update_video_record(video)
            # 告警
            notice_text = f"[Youtube Crawler | ERROR] download pipeline failed. \
                \n\t下载服务: {SERVER_NAME} | {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count}\
                \n\t资源ID: {video.id} | {video.vid} \
                \n\tSource_Link: {video.source_link} \
                \n\tCloud_Link: {video.cloud_path} \
                \n\t共处理了{format_second_to_time_string(int(time_fail-time_1))} \
                \n\tIP: {local_ip} | {get_public_ip()} \
                \n\tERROR: {e} \
                \n\t告警时间: {get_now_time_string()}"
            logger.error(notice_text)
            alarm_lark_text(webhook=getenv("LARK_NOTICE_WEBHOOK"), text=notice_text)
            # 失败过多直接退出
            if continue_fail_count > LIMIT_FAIL_COUNT:
                logger.error(f"Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
                alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
                exit()
            youtube_sleep(is_succ=False, run_count=run_count, download_round=download_round)
            continue
        else:
            continue_fail_count = 0
            # 告警
            notice_text = f"[Youtube Crawler | DEBUG] download pipeline succeed. \
                \n\t下载服务: {SERVER_NAME} | {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count} \
                \n\tLink: {video.source_link} -> {video.cloud_path} \
                \n\t资源共 {file_size:.2f}MB , 共处理了{format_second_to_time_string(spend_total_time)} \
                \n\t下载时长: {format_second_to_time_string(spend_download_time)} , 上传时长: {format_second_to_time_string(spend_upload_time)} \
                \n\t下载均速: {file_size/spend_download_time:.2f}M/s , 上传均速: {file_size/spend_upload_time:.2f}M/s \
                \n\tIP: {local_ip} | {get_public_ip()}"
            logger.info(notice_text)
            alarm_lark_text(webhook=getenv("LARK_NOTICE_WEBHOOK"), text=notice_text)
            youtube_sleep(is_succ=True, run_count=run_count, download_round=download_round)
        finally:
            download_round = run_count//LIMIT_LAST_COUNT + 1
            # clean_temp_files(vid)


if __name__ == "__main__":
    import multiprocessing
    from sys import exit
    # PROCESS_NUM = 1 #同时处理的进程数量
    PROCESS_NUM = getenv("PROCESS_NUM")
    PROCESS_NUM = int(PROCESS_NUM)

    with multiprocessing.Pool(PROCESS_NUM) as pool:
        pool.map(main_pipeline, range(PROCESS_NUM))
    exit(0)

    # main_pipeline(0)