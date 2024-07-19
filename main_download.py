# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

import os
from handler.youtube import format_into_watch_url
from handler.youtube import download as ytb_download
from handler.bilibili import download as bilibili_download
from handler.ximalaya import download as ximalaya_download
from utils import logger

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
        audio_path = ytb_download(full_url, os.getenv('DOWNLOAD_PATH'))
        logger.info(f"Downloaded youtube audio to {audio_path}")
    elif item_type == "bilibili":
        pass
        # audio_path = bilibili_download(full_url, cfg["common"]["download_path"])
        logger.info(f"Downloaded bilibili audio to {audio_path}")
    elif item_type == "ximalaya" or item_type == "xmcdn":
        pass
        # audio_path = ximalaya_download(
        #     full_url,
        #     cfg["common"]["download_path"],
        #     is_xmcdn=item_type == "xmcdn",
        # )
        logger.info(f"Downloaded ximalaya audio to {audio_path}")
    return audio_path


def main():
    # 调用接口获取待处理数据

    # 油管链接格式化
    # url = "https://www.youtube.com/watch?v=tXuPmu2Sa60&list=PLRMEKqidcRnBaMTFQzWkXpNk8_xF3QvMZ"
    # url = "https://www.youtube.com/watch?v=tXuPmu2Sa60"
    url = "https://www.youtube.com/watch?v=6s416NmSFmw&list=PLRMEKqidcRnAGC6j1oYPFV9E26gyWdgU4&index=4"
    url = format_into_watch_url(url)

    # 下载处理
    download(url)

    

if __name__ == "__main__":
    main()