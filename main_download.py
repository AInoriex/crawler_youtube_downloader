# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import os
import time
from urllib.parse import urljoin
from handler.youtube import format_into_watch_url
from handler.youtube import download as ytb_download
# from handler.bilibili import download as bilibili_download
# from handler.ximalaya import download as ximalaya_download
# from database import handler as dao
from database.youtube_api import get_download_list, update_status
from utils import logger
from utils.utime import random_sleep, get_now_time_string
from utils.file import get_file_size
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
# from utils.cos import upload_file
from utils.obs import upload_file

# 初始化
logger = logger.init_logger("main_download")

# 分析url链接视频来源
def detect_type(data):
    # bilibili, youtube, ximalaya
    keywords = ["bilibili", "youtube", "ximalaya", "xmcdn"]
    for keyword in keywords:
        if keyword in data:
            return keyword
    return None

# 下载url链接资源
def download(full_url):
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


def database_pipeline(pid):
    time.sleep(15 * pid)
    logger.debug(f"Pipeline > pid {pid} started")
    wait_flag = False

    while True:
        # id, _, link, _ = dao.get_next_audio(
        #     f"WHERE status = 0 AND `lock` = 0 AND `language` = 'vt' AND `source_type` = 3"
        # )
        video = get_download_list()

        # if id is None:
        if video is None:
            if not wait_flag:
                logger.info(f"Pipeline > pid {pid} no task, waiting...")
                wait_flag = True
            random_sleep(rand_st=20, rand_range=10)
            continue
        wait_flag = False
        id = video.id
        link = video.source_link

        try:
            logger.info(f"Pipeline > pid {pid} processing {id} -- {link}")
            time_st = time.time()

            # 下载(本地存在不会被覆盖)
            link = format_into_watch_url(link)
            download_path = download(link)
            # cloud_path = os.path.join(os.getenv("OBS_SAVEPATH"), os.path.basename(download_path))
            cloud_path = urljoin(os.getenv("OBS_SAVEPATH"), os.path.basename(download_path))
            
            # 上传云端
            cloud_link = upload_file(
                from_path=download_path, to_path=cloud_path
            )
            
            # 更新数据库
            # dao.uploaded_download(
            #     id=id, 
            #     cloud_type=2,
            #     cloud_path=cloud_link, 
            #     # path=download_path
            # )
            video.status = 2 # upload done
            video.cloud_type = 2 # 1:cos 2:obs
            video.cloud_path = cloud_link
            update_status(video)
            
            # LOG
            time_ed = time.time()
            logger.info(
                f"Pipeline > pid {pid} done processing {id}, uploaded to {cloud_path}, file_size:  %.2f MB, spend_time: %.2f seconds" \
                %(get_file_size(download_path), time_ed - time_st) \
            )
            
            # 移除本地文件
            os.remove(download_path)
        except KeyboardInterrupt:
            logger.warning(f"Pipeline > pid {pid} interrupted processing {id}, reverting...")
            # revert lock to 0
            # dao.revert_audio(id)
            video.lock = 0
            update_status(video)
            break
        except Exception as e:
            logger.error(f"Pipeline > pid {pid} error processing {id}")
            logger.error(e, stack_info=True)
            # dao.failed_audio(id)
            video.status = -1
            video.lock = 0
            update_status(video)
            # alarm to Lark Bot
            now_str = get_now_time_string()
            local_ip = get_local_ip()
            public_ip = get_public_ip()
            notice_text = f"[Youtube Crawler | ERROR] download pipeline failed. \
                \n\t进程ID: {pid} \
                \n\tId: {video.id}  \
                \n\tVid: {video.vid} \
                \n\tSource_Link: {video.source_link} \
                \n\tCloud_Link: {video.cloud_path} \
                \n\tLocal_IP: {local_ip} \
                \n\tPublic_IP: {public_ip} \
                \n\tERROR: {e} \
                \n\tTime: {now_str}"
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
            random_sleep(rand_st=60*5, rand_range=60*5) #请求失败等待05-10mins
            continue
        else:
            # alarm to Lark Bot
            local_ip = get_local_ip()
            public_ip = get_public_ip()
            notice_text = f"[Youtube Crawler | DEBUG] download pipeline succeed. \
                \n\t进程ID: {pid} \
                \n\tSource_Link: {video.source_link} \
                \n\tCloud_Link: {video.cloud_path} \
                \n\tIP: {local_ip} | {public_ip}"
            alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
            random_sleep(rand_st=25, rand_range=25) #成功间隔25s以上


if __name__ == "__main__":
    import multiprocessing
    from sys import exit
    # PROCESS_NUM = 1 #同时处理的进程数量
    PROCESS_NUM = os.getenv("PROCESS_NUM")
    PROCESS_NUM = int(PROCESS_NUM)

    with multiprocessing.Pool(PROCESS_NUM) as pool:
        pool.map(database_pipeline, range(PROCESS_NUM))
    exit(0)

    # database_pipeline(1)