# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import os
import time
from urllib.parse import urljoin
from handler.youtube import format_into_watch_url, is_touch_fish_time
from handler.youtube import download as ytb_download
# from handler.bilibili import download as bilibili_download
# from handler.ximalaya import download as ximalaya_download
from database.youtube_api import get_download_list, update_status
from utils import logger
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.file import get_file_size
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
# from utils.cos import upload_file
from utils.obs import upload_file

# -----------------
# ---- 初始化 -----
# -----------------

logger = logger.init_logger("main_download")

LIMIT_FAIL_COUNT = int(os.getenv("LIMIT_FAIL_COUNT"))
# LIMIT_FAIL_COUNT = 10
''' 处理失败任务限制数 '''
LIMIT_LAST_COUNT = int(os.getenv("LIMIT_LAST_COUNT"))
# LIMIT_LAST_COUNT = 100
''' 连续处理任务限制数 '''


def detect_type(data):
    ''' 解析url链接视频来源 '''
    # bilibili, youtube, ximalaya
    keywords = ["bilibili", "youtube", "ximalaya", "xmcdn"]
    for keyword in keywords:
        if keyword in data:
            return keyword
    return None

def download(full_url):
    ''' 下载url链接资源 '''
    logger.info(f"当前下载链接：{full_url}")
    item_type = detect_type(full_url)
    if item_type is None:
        logger.error(f"Failed to detect item type: {full_url}")
        return None
    elif item_type == "youtube":
        download_path = ytb_download(full_url, os.getenv('DOWNLOAD_PATH'))
        logger.info(f"Downloaded youtube audio to {download_path}")
    elif item_type == "bilibili":
        pass
        # audio_path = bilibili_download(full_url, cfg["common"]["download_path"])
        logger.info(f"Downloaded bilibili audio to {download_path}")
    elif item_type == "ximalaya" or item_type == "xmcdn":
        pass
        # audio_path = ximalaya_download(
        #     full_url,
        #     cfg["common"]["download_path"],
        #     is_xmcdn=item_type == "xmcdn",
        # )
        logger.info(f"Downloaded ximalaya audio to {download_path}")
    return download_path

def youtube_sleep(is_succ:bool, run_count:int, download_round:int):
    """ 油管下载间隔等待规则 """
    now_round = run_count//LIMIT_LAST_COUNT + 1
    if now_round > download_round:
        logger.info(f"Pipeline > 触发轮数限制, 当前轮数：{now_round}")
        random_sleep(rand_st=60*20, rand_range=1) #每轮固定等20mins
        return

    if is_succ:
        if is_touch_fish_time():
            random_sleep(rand_st=25, rand_range=25) #处理成功间隔25s以上
        else:
            random_sleep(rand_st=60, rand_range=30) #处理成功间隔60s以上(非摸鱼时间)
    else:
        if is_touch_fish_time():
            random_sleep(rand_st=60*5, rand_range=60*5) #请求失败等待05-10mins
        else:
            random_sleep(rand_st=60*10, rand_range=60*20) #请求失败等待10-30mins(非摸鱼时间)


def database_pipeline(pid):
    time.sleep(15 * pid)
    logger.debug(f"Pipeline > pid {pid} started")
    wait_flag = False
    download_round = 1      # 当前下载轮数
    run_count = 0           # 持续处理的任务个数
    continue_fail_count = 0 # 连续失败的任务个数

    while True:
        video = get_download_list(query_id=0)
        # video = get_download_list(query_id=4898)

        if video is None:
            if not wait_flag:
                logger.info(f"Pipeline > pid {pid} no task which has processed {run_count} tasks, waiting...")
                wait_flag = True
            random_sleep(rand_st=20, rand_range=10)
            continue
        wait_flag = False
        id = video.id
        link = video.source_link

        try:
            run_count += 1
            logger.info(f"Pipeline > pid {pid} processing {id} -- {link}, 轮数 {download_round} | 处理数 {run_count}")
            time_1 = time.time()

            # 下载(本地存在不会被覆盖，续传)
            # random_sleep(5, 3)
            link = format_into_watch_url(link)
            download_path = download(link)
            cloud_path = urljoin(os.getenv("OBS_SAVEPATH"), os.path.basename(download_path))
            time_2 = time.time()
            spend_download_time = int(time_2 - time_1) #下载花费时间
            
            # 上传云端
            # random_sleep(5, 3)
            cloud_link = upload_file(
                from_path=download_path, to_path=cloud_path
            )
            time_3 = time.time()
            spend_upload_time = int(time_3 - time_2) #上传花费时间
            
            # 更新数据库
            video.status = 2 # upload done
            video.cloud_type = 2 # 1:cos 2:obs
            video.cloud_path = cloud_link
            update_status(video)
            
            # 日志记录
            spend_total_time = int(time_3 - time_1) #总花费时间
            file_size = get_file_size(download_path)
            logger.info(
                f"Pipeline > pid {pid} done processing {id}, uploaded to {cloud_path}, \
                    file_size: {file_size} MB, spend_time: {format_second_to_time_string(spend_total_time)} seconds"
            )
            
            # 移除本地文件
            os.remove(download_path)

        except KeyboardInterrupt:
            logger.warning(f"Pipeline > pid {pid} interrupted processing {id}, reverting...")
            # revert lock to 0
            video.lock = 0
            update_status(video)
            break
        except Exception as e:
            continue_fail_count += 1
            time_fail = time.time()
            logger.error(f"Pipeline > pid {pid} error processing {id}")
            logger.error(e, stack_info=True)
            # 任务回调
            video.status = -1
            video.lock = 0
            update_status(video)
            # 告警
            now_str = get_now_time_string()
            local_ip = get_local_ip()
            public_ip = get_public_ip()
            notice_text = f"[Youtube Crawler | ERROR] download pipeline failed. \
                \n\t进程ID: {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count}\
                \n\t资源ID: {video.id} | {video.vid} \
                \n\tSource_Link: {video.source_link} \
                \n\tCloud_Link: {video.cloud_path} \
                \n\t资源共 {file_size}MB , 共处理了{format_second_to_time_string(int(time_fail-time_1))} \
                \n\tIP: {local_ip} | {public_ip} \
                \n\tERROR: {e} \
                \n\t告警时间: {now_str}"
            logger.error(notice_text)
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
            # 失败过多直接退出
            if continue_fail_count > LIMIT_FAIL_COUNT:
                logger.error(f"Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
                exit()
            youtube_sleep(is_succ=False, run_count=run_count, download_round=download_round)
            continue
        else:
            continue_fail_count = 0
            # 告警
            local_ip = get_local_ip()
            public_ip = get_public_ip()
            notice_text = f"[Youtube Crawler | DEBUG] download pipeline succeed. \
                \n\t进程ID: {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count} \
                \n\tLink: {video.source_link} -> {video.cloud_path} \
                \n\t资源共 {file_size}MB , 共处理了{format_second_to_time_string(spend_total_time)} \
                \n\t下载时长: {format_second_to_time_string(spend_download_time)} , 上传时长: {format_second_to_time_string(spend_upload_time)} \
                \n\t下载均速: {round(file_size/spend_download_time, 2)}M/s , 上传均速: {round(file_size/spend_upload_time, 2)}M/s \
                \n\tIP: {local_ip} | {public_ip}"
            logger.info(notice_text)
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
            youtube_sleep(is_succ=True, run_count=run_count, download_round=download_round)
        finally:
            download_round = run_count//LIMIT_LAST_COUNT + 1


if __name__ == "__main__":
    # import multiprocessing
    # from sys import exit
    # # PROCESS_NUM = 1 #同时处理的进程数量
    # PROCESS_NUM = os.getenv("PROCESS_NUM")
    # PROCESS_NUM = int(PROCESS_NUM)

    # with multiprocessing.Pool(PROCESS_NUM) as pool:
    #     pool.map(database_pipeline, range(PROCESS_NUM))
    # exit(0)

    database_pipeline(0)