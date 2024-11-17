# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import json
from os import getenv, path, remove
from time import time, sleep
from urllib.parse import urljoin
from traceback import format_exc
from handler.youtube import is_touch_fish_time, get_cloud_save_path_by_language
from handler.yt_dlp import clean_path
from handler.youtube_accout import YoutubeAccout
# from handler.bilibili import download as bilibili_download
# from handler.ximalaya import download as ximalaya_download
from database.youtube_api import get_video_for_download, update_video_record
from utils import logger as ulogger
from utils.utime import random_sleep, get_now_time_string, format_second_to_time_string
from utils.file import get_file_size
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip

# ---------------------
# ---- 初始化参数 -----
# ---------------------

local_ip = get_local_ip()
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
    from utils.obs import upload_file as obs_upload_file
    from utils.obs import upload_file_v2 as obs_upload_file_v2
elif CLOUD_TYPE == "cos":
    from utils.cos import upload_file as cos_upload_file
else:
    raise NotImplementedError
DOWNLOAD_PATH = getenv('DOWNLOAD_PATH')
''' YouTube资源下载目录'''
OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
''' YouTube账号缓存目录'''
print("main > 初始化完毕")

# ---------------------------------------------------------------

def youtube_sleep(is_succ:bool, run_count:int, download_round:int):
    """
    任务处理 sleep 机制

    :param is_succ: bool, 任务是否处理成功
    :param run_count: int, 任务处理次数
    :param download_round: int, 任务处理轮数

    1. 触发轮数限制,每轮固定等2mins
    2. 任务处理成功
        2.1.摸鱼时间,间隔5s以上
        2.2.非摸鱼时间,间隔10s以上
    3. 任务处理失败
        3.1.摸鱼时间,等待0.5mins以上
        3.2.非摸鱼时间,等待1mins以上
    """
    now_round = run_count//LIMIT_LAST_COUNT + 1
    if now_round > download_round:
        print(f"Pipeline > 触发轮数限制, 当前轮数：{now_round}")
        random_sleep(rand_st=60, rand_range=30)
        return
    if is_succ:
        if is_touch_fish_time():
            random_sleep(rand_st=5, rand_range=10)
        else:
            random_sleep(rand_st=10, rand_range=10)
    else:
        if is_touch_fish_time():
            random_sleep(rand_st=5, rand_range=20)
        else:
            random_sleep(rand_st=10, rand_range=20)

def download_with_yt_dlp(video, save_path):
    from handler.yt_dlp import download_by_watch_url
    download_path = download_by_watch_url(video, save_path=save_path)
    if download_path == "":
        raise("download_with_yt_dlp download_path empty")
    return download_path

def download_with_tubedown(video, save_path):
    from handler.tubedown import extract_download_url, get_url_resource, get_url_resource_v2
    from handler.tubedown import get_youtube_vid, get_mime_type
    # 解析
    down_info = extract_download_url(video.source_link)
    dst_url = down_info.get("video_info", {}).get("url")
    # audio_url = down_info.get("audio_info", {}).get("url")
    # logger.info(f"视频下载地址：{video_url}")
    # logger.info(f"音频下载地址：{audio_url}")

    # 下载
    filename = path.join(save_path, f"{get_youtube_vid(video.source_link)}.{get_mime_type(dst_url, default='mp4')}")
    # download_path = get_url_resource(dst_url, filename)
    download_path = get_url_resource_v2(dst_url, filename)
    if download_path == "":
        raise("download_with_tubedown download_path empty")
    return download_path

def youtube_download_handler(video, save_path):
    if getenv("YTB_DOWNLOAD_MODE", "") == "tubedown":
        print("youtube_download_handler > 当前下载模式: tubedown")
        return download_with_tubedown(video, save_path)
    elif getenv("YTB_DOWNLOAD_MODE", "") == "yt_dlp":
        print("youtube_download_handler > 当前下载模式: yt_dlp")
        return download_with_yt_dlp(video, save_path)
    else:
        print("youtube_download_handler > 未配置下载模式, 默认 yt_dlp")
        return download_with_yt_dlp(video, save_path)

def main_pipeline(pid, ac:YoutubeAccout):
    logger = ulogger.init_logger("main_pipeline")
    logger.info(f"youtube_account > 初始化账号cache路径：{OAUTH2_PATH}")
    sleep(15 * pid)
    logger.debug(f"Pipeline > 进程 {pid} 开始执行, 当前账号: {ac.get_account_info()}")
    download_round = int(1)      # 当前下载轮数
    run_count = int(0)           # 持续处理的任务个数
    continue_fail_count = int(0) # 连续失败的任务个数

    while True:
        video = get_video_for_download(
            query_id=0, 
            query_source_type=int(getenv("DOWNLOAD_SOURCE_TYPE")),
            query_language=getenv("DOWNLOAD_LANGUAGE"),
        )
        # video = get_video_for_download(query_id=668925)

        if video is None:
            logger.warning(f"Pipeline > 进程 {pid} 无任务待处理, 当前轮次: {download_round} | {run_count}, 等待中...")
            random_sleep(rand_st=20, rand_range=10)
            continue
        if video.id <= 0 or video.source_link == "":
            logger.warning(f"Pipeline > 进程 {pid} 获取无效任务, 跳过处理...")
            random_sleep(rand_st=20, rand_range=10)
            continue
        try:
            video_id = video.id
            video_link = video.source_link
            if video.info != "":
                info = json.loads(video.info)
                cloud_save_path = info.get("cloud_save_path", "")
            else:
                cloud_save_path = ""
            run_count += 1
            logger.info(f"Pipeline > 进程 {pid} 处理任务 {video_id} -- {video_link}, 当前轮次: {download_round} | {run_count}")

            # 下载
            time_1 = time()
            download_path = youtube_download_handler(video, DOWNLOAD_PATH)
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
                f"Pipeline > 进程 {pid} 完成处理任务 {video_id}, 已上传至 {cloud_path}, 文件大小: {file_size} MB, 共处理了 {format_second_to_time_string(spend_total_time)}"
            )
            
            # 移除本地文件
            remove(download_path)

        except KeyboardInterrupt:
            logger.warning(f"Pipeline > 进程 {pid} interrupted processing {video_id}, reverting...")
            # 任务回调
            video.lock = 0
            update_video_record(video)
            # return
            # break
            raise KeyboardInterrupt
        except BrokenPipeError as e: # 账号被封处理
            continue_fail_count += 1
            time_fail = time()
            logger.error(f"Pipeline > 进程 {pid} 处理任务 {video_id} 失败, 账号可能失效")
            logger.error(e, stack_info=True)
            # 任务回调
            video.status = -1
            video.lock = 0
            update_video_record(video)
            # 告警
            notice_text = f"[Youtube Crawler | ERROR] 账号失效. \
                \n\t下载服务: {SERVER_NAME} | {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count} \
                \n\t资源信息: {video.id} | {video.vid} | {video.language} \
                \n\tSource_Link: {video.source_link} \
                \n\tError: {e} \
                \n\t共处理了{format_second_to_time_string(int(time_fail-time_1))} \
                \n\tIP: {local_ip} | {get_public_ip()} \
                \n\t账号信息: {ac.get_account_info()} \
                \n\t告警时间: {get_now_time_string()}"
            logger.error(notice_text)
            alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
            # 登出账号
            if getenv("CRAWLER_SWITCH_ACCOUNT_ON", False) == "True":
                ac.logout(is_invalid=True, comment="账号失效") 
            # 失败过多直接退出
            if continue_fail_count > LIMIT_FAIL_COUNT:
                logger.error(f"Pipeline > 进程 {pid} 失败过多超过{continue_fail_count}次, 异常退出")
                return
            
            # 暂不支持自动切换号
            return
            # 换号
            # if getenv("CRAWLER_SWITCH_ACCOUNT_ON", False) == "True":
            #     if ac.is_process:
            #         logger.warning(f"Pipeline > [!] 当前正在换号中")
            #         youtube_sleep(is_succ=False, run_count=run_count, download_round=download_round)
            #     else:
            #         logger.warning(f"Pipeline > [!] 开始尝试切换新账号使用")
            #         handler_switch_account(ac)
            # else:
            #     logger.info(f"Pipeline > [!] 当前未开启自动切换账号模式")
            # continue
        except Exception as e:
            continue_fail_count += 1
            time_fail = time()
            logger.error(f"Pipeline > 进程 {pid} 处理任务 {video_id} 失败, 错误信息:{e}")
            logger.error(e, stack_info=True)
            # 任务回调
            video.status = -1
            video.lock = 0
            update_video_record(video)
            # 告警
            notice_text = f"[Youtube Crawler | ERROR] download pipeline failed. \
                \n\t下载服务: {SERVER_NAME} | {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count}\
                \n\t资源信息: {video.id} | {video.vid} | {video.language} \
                \n\tSource Link: {video.source_link} \
                \n\tCloud Link: {video.cloud_path} \
                \n\t共处理了{format_second_to_time_string(int(time_fail-time_1))} \
                \n\tIP: {local_ip} | {get_public_ip()} \
                \n\tError: {e.__class__} | {e} \
                \n\t告警时间: {get_now_time_string()} \
                \n\tStack Info: {format_exc()}"
            logger.error(notice_text)
            alarm_lark_text(webhook=getenv("LARK_NOTICE_WEBHOOK"), text=notice_text)
            # 失败过多直接退出
            if continue_fail_count > LIMIT_FAIL_COUNT:
                logger.error(f"Pipeline > 进程 {pid} 失败过多超过{continue_fail_count}次, 异常退出")
                alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
                # 退出登陆
                if getenv("CRAWLER_SWITCH_ACCOUNT_ON", False) == "True":
                    ac.logout(is_invalid=True, comment=f"{SERVER_NAME}失败过多退出, {e}")
                return
            youtube_sleep(is_succ=False, run_count=run_count, download_round=download_round)
            continue
        else:
            continue_fail_count = 0
            # 告警
            notice_text = f"[Youtube Crawler | DEBUG] download pipeline succeed. \
                \n\t下载服务: {SERVER_NAME} | 进程: {pid} \
                \n\t下载信息: 轮数 {download_round} | 处理总数 {run_count} | 连续失败数 {continue_fail_count} \
                \n\t资源信息: {video.id} | {video.vid} | {video.language} \
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

def handle_switch_account()->YoutubeAccout:
    """
    账号轮询登陆直至成功

    :param ac: YoutubeAccout, 账号实例
    :return: None
    """
    logger = ulogger.init_logger("handle_switch_account")
    while 1:
        try:
            ac = YoutubeAccout()
            ac.youtube_login_handler() # 需要登陆成功才能继续处理
        except Exception as e:
            logger.error(f"Pipeline > 初始化账号出错, 等待30s重试, traceback: {format_exc()}")
            sleep(30)
            continue
        else:
            logger.info(f"Pipeline > 初始化账号成功，{ac.id} | {ac.username}")
            break
    return ac

if __name__ == "__main__":
    # 初始化账号
    ac = YoutubeAccout()
    if OAUTH2_PATH == "":
        if getenv("CRAWLER_SWITCH_ACCOUNT_ON", False) == "True":
            print("main > 账号为空，准备初始化账号")
            ac = handle_switch_account()
        else:
            print("main > [!] 当前OAuth2账号为空")

    # 清理旧目录文件
    clean_path(DOWNLOAD_PATH)

    import multiprocessing
    # PROCESS_NUM = 1 #同时处理的进程数量
    PROCESS_NUM = getenv("PROCESS_NUM")
    PROCESS_NUM = int(PROCESS_NUM)

    try:
        with multiprocessing.Pool(PROCESS_NUM) as pool:
            for i in range(PROCESS_NUM):
                pool.apply_async(main_pipeline, (i, ac))
            pool.close()
            pool.join()
            # pool.terminate()
        # main_pipeline(0)
    except Exception as e:
        print(f"main > Exception raise: {e.__class__} | {e}")
        pool.terminate()