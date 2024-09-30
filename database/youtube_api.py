# import sys
# import os
# work_dir = os.path.realpath(os.path.dirname(sys.argv[0]))
# sys.path.append(os.path.join(work_dir, ".."))

# from uuid import uuid4
# from time import time
from os import getenv
from requests import get, post
from utils.utime import get_time_stamp
from database.handler import Video

def get_video_for_download(query_id=0, query_source_type=int(getenv("DOWNLOAD_SOURCE_TYPE")), query_language=getenv("DOWNLOAD_LANGUAGE"))->Video|None:
    ''' 获取一条ytb记录
    @API    get_video_for_download
    '''
    try:
        url = getenv("DATABASE_GET_API")
        params = {
            "sign": get_time_stamp(),
            # "sign": int(time()),
            "id": query_id,
            "source_type": query_source_type,
            "language": query_language,
            "limit": 1
        }
        # print(f"get_video_for_download > Get list Request | url:{url} params:{params}")
        resp = get(url=url, params=params)
        print(f"get_video_for_download > Get list Response | status_code:{resp.status_code}, content:{resp.content}")
        assert resp.status_code == 200
        resp_json = resp.json()
        # print("get_video_for_download > Get list Response detail | status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
        if len(resp_json["data"]["result"]) <= 0:
            print("get_video_for_download > get nothing.")
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
        )
    except Exception as e:
        print(f"get_video_for_download > Error: {e}")
        raise Exception(f"get_video_for_download failed, req:{params}, resp:{resp_json}")
    else:
        return video

def update_video_record(video:Video):
    ''' 更新ytb记录
    @API    update_video_record
    '''
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
    }
    # print(f"update_video_record > Update Request | url:{url} params:{params} body:{reqbody}")
    resp = post(url=url, params=params, json=reqbody)
    assert resp.status_code == 200
    resp_json = resp.json()
    # print("update_video_record > Update Response | status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    resp_code = resp_json["code"]
    if resp_code != 0:
        raise Exception(f"update_video_record failed, req:{reqbody}, resp:{resp_json}")
    else:
        print(f"update_video_record > update succeed, req:{reqbody}")

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