# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

from os import path, makedirs, getenv
from time import time, sleep
from handler.youtube import download_by_playlist_url, download_url
from utils.logger import logger
from utils.utime import get_now_time_string, format_second_to_time_string
from utils.lark import alarm_lark_text

# logger = logger.init_logger("main_download")

# SERVER_NAME = "local_download_test"
SERVER_NAME =  getenv("SERVER_NAME")
TASK_NAME = getenv("YTB_DOWNLOAD_FILE")

# 本地文件批量下载播放列表下所有视频
def local_download_pipeline():
    with open(TASK_NAME, "r") as file:
        download_urls = file.read().splitlines()
    
    ans = input(f"待下载 {TASK_NAME} 文件共{len(download_urls)}条，确认下载 【输入：")
    if ans not in ["y", "Y", "yes", "Yes", "YES"]:
        print(f"[INFO] 输入：{ans}, EXIT")
        exit(0)
    count = 0
    for url in download_urls:
        count += 1
        print(f"local_download_pipeline > 当前下载链接: {url}")
        sleep(1)
        try:
            time_1 = time()
            # playlist_url="https://www.youtube.com/playlist?list=PLJaq64dKJZorN3offUhO22yfKx5NkWGE8"
            result = download_url(
                url=url,
                save_path=getenv("DOWNLOAD_PATH")
            )
        except Exception as e:
            # 告警
            notice_text = f"[Youtube Crawler | ERROR] download pipeline failed. \
                \n\t下载服务: {SERVER_NAME} \
                \n\tSource_Link: {url} \
                \n\t进度: {count} | {len(download_urls)} \
                \n\t处理时长: {format_second_to_time_string(int(time()-time_1))} \
                \n\tERROR: {e} \
                \n\t告警时间: {get_now_time_string()}"
            logger.error(notice_text)
            alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
        else:
            # 告警
            notice_text = f"[Youtube Crawler | DEBUG] download pipeline successful. \
                \n\t下载服务: {SERVER_NAME} \
                \n\tSource_Link: {url} \
                \n\tResult: {result} \
                \n\t进度: {count} | {len(download_urls)} \
                \n\t处理时长: {format_second_to_time_string(int(time()-time_1))} \
                \n\t告警时间: {get_now_time_string()}"
            logger.error(notice_text)
            alarm_lark_text(webhook=getenv("LARK_NOTICE_WEBHOOK"), text=notice_text)


if __name__ == "__main__":
    local_download_pipeline()