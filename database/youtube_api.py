# import sys
# import os
# work_dir = os.path.realpath(os.path.dirname(sys.argv[0]))
# sys.path.append(os.path.join(work_dir, ".."))

# from uuid import uuid4
# from time import time
from os import getenv
from requests import get, post
from utils.utime import get_time_stamp
from utils.logger import logger
from database.crawler_download_info import Video

def get_video_for_download(
        query_id=0,
        query_source_type=int(getenv("DOWNLOAD_SOURCE_TYPE")),
        query_language=getenv("DOWNLOAD_LANGUAGE"),
    )->Video|None:
    """
    get a video for downloading from `DATABASE_GET_API` in .env

    :param query_id: int, video id in database, default is 0 which means get a random video
    :param query_source_type: int, source type of video, default is `DOWNLOAD_SOURCE_TYPE` in .env
    :param query_language: str, language of video, default is `DOWNLOAD_LANGUAGE` in .env
    :return: Video or None
    """
    try:
        url = getenv("DATABASE_GET_API")
        params = {
            "sign": get_time_stamp(),
            "id": query_id,
            "source_type": query_source_type,
            "language": query_language,
            "limit": 1
        }
        # logger.debug(f"get_video_for_download > Get list Request | url:{url} params:{params}")
        resp = get(url=url, params=params)
        # logger.debug(f"get_video_for_download > Get list Response | status_code:{resp.status_code}, content:{str(resp.content, encoding='utf-8')}")
        assert resp.status_code == 200
        resp_json = resp.json()
        logger.debug(f"get_video_for_download > Get list Response detail | status_code:{resp_json['code']}, content:{resp_json['msg']}")
        if len(resp_json["data"]["result"]) <= 0:
            logger.warning("get_video_for_download > No video to download")
            return None
        resp_data:dict = resp_json["data"]["result"][0]
        video = Video(
            id=resp_data.get("id", 0),
            vid=resp_data.get("vid", ""),
            position=resp_data.get("position", 0),
            source_type=resp_data.get("source_type", 0),
            source_link=resp_data.get("source_link", ""),
            duration=resp_data.get("duration", 0),
            cloud_type=resp_data.get("cloud_type", 0),
            cloud_path=resp_data.get("cloud_path", ""),
            language=resp_data.get("language", ""),
            status=resp_data.get("status", 0),
            lock=resp_data.get("lock", 0),
            info=resp_data.get("info", ""),
            comment=resp_data.get("comment", "")
        )
        return video
    except Exception as e:
        logger.error(f"get_video_for_download > get video failed, url:{url}, req:{params}, error: {e}")
        return None

def update_video_record(video:Video):
    """
    update a video record in database with `DATABASE_UPDATE_API` in .env

    :param video: Video, the video record to be updated
    :return: None
    """
    
    url = getenv("DATABASE_UPDATE_API")
    params = {
        "sign": get_time_stamp()
    }
    reqbody = {
        "id": video.id,
        # "vid": video.vid,
        "status": video.status,
        "cloud_type": video.cloud_type,
        "cloud_path": video.cloud_path,
        "comment": video.comment,
    }
    # logger.debug(f"update_video_record > update request | url:{url} params:{params} body:{reqbody}")
    resp = post(url=url, params=params, json=reqbody)
    assert resp.status_code == 200
    resp_json = resp.json()
    # logger.debug("update_video_record > update response | status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    if resp_json["code"] != 0:
        raise Exception(f"update_video_record failed, req:{reqbody}, resp:{resp.status_code}|{str(resp.content, encoding='utf-8')}")
    else:
        logger.info(f"update_video_record > update succeed, req:{reqbody}")

if __name__ == "__main__":
    # 测试获取一条ytb记录
    v = get_video_for_download(
        query_id=0,
        query_source_type=7,
        query_language="vi"
    )
    print("get_video_for_download debug:", v.__str__)
    
    # 测试更新ytb记录
    v.cloud_type = 10
    v.cloud_path = "https://www.youtube.com/watch?v=nothing"
    update_video_record(v)