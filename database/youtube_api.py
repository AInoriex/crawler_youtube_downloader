from utils.utime import get_time_stamp
from requests import get, post
from uuid import uuid4
from database.handler import Video
from os import getenv

def get_download_list(query_id=0)->Video|None:
    ''' 获取一条ytb记录 '''
    url = getenv("DATABASE_GET_API")
    params = {
        "sign": get_time_stamp(),
        "id": query_id
    }
    # print(f"Ytb_db_api > Get list Request | url:{url} params:{params}")
    resp = get(url=url, params=params)
    print(f"Ytb_db_api > Get list Response | status_code:{resp.status_code}, content:{resp.content}")
    assert resp.status_code == 200
    resp_json = resp.json()
    # print("Ytb_db_api > Get list Response detail | status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    if len(resp_json["data"]["result"]) <= 0:
        # print("Ytb_db_api > Nothing to get.")
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
    return video

def update_status(video:Video):
    ''' 更新ytb记录 '''
    url = getenv("DATABASE_UPDATE_API")
    params = {
        "sign": get_time_stamp()
    }
    reqbody = {
        "id": video.id,
        "vid": video.vid,
        "status": video.status,
        "cloud_type": video.cloud_type,
        "cloud_path": video.cloud_path,
    }
    # print(f"Ytb_db_api > Update Request | url:{url} params:{params} body:{reqbody}")
    resp = post(url=url, params=params, json=reqbody)
    assert resp.status_code == 200
    resp_json = resp.json()
    # print("Ytb_db_api > Update Response | status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    resp_code = resp_json["code"]
    if resp_code != 0:
        raise Exception(f"更新数据接口失败, req:{reqbody}, resp:{resp_json}")
    else:
        print("Ytb_db_api > 更新状态成功 req:%s"%reqbody)

if __name__ == "__main__":
    v = get_download_list()