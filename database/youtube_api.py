from utils.utime import get_time_stamp
from requests import get, post
from uuid import uuid4
from database.handler import Video
from os import getenv

def get_download_list()->Video|None:
    ''' 随机获取一条ytb记录 '''
    url = "%s?sign=%d"%(getenv("DATABASE_GET_API"), get_time_stamp())
    # print(f"YoutubeGetDownloadList req, url:{url}")
    resp = get(url=url)
    print(f"YoutubeGetDownloadList resp, status_code:{resp.status_code}, content:{resp.content}")
    assert resp.status_code == 200
    resp_json = resp.json()
    # print("YoutubeGetDownloadList resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    if len(resp_json["data"]["result"]) <= 0:
        print("YoutubeGetDownloadList nothing to get.")
        return None
    resp_data = resp_json["data"]["result"][0]
    video = Video(
        id=resp_data["id"],
        vid=resp_data["vid"],
        position=resp_data["position"],
        source_type=resp_data["source_type"],
        source_link=resp_data["source_link"],
        duration=resp_data["duration"],
        cloud_type=resp_data["cloud_type"],
        cloud_path=resp_data["cloud_path"],
        language=resp_data["language"],
        status=resp_data["status"],
        lock=resp_data["lock"],
        info=resp_data["info"],
    )
    return video

def update_status(video:Video):
    ''' 更新ytb记录 '''
    url = getenv("DATABASE_UPDATE_API")
    req = {
        "id": video.id,
        "vid": video.vid,
        "status": video.status,
        "cloud_type": video.cloud_type,
        "cloud_path": video.cloud_path,
    }

    resp = post(url=url, json=req)
    assert resp.status_code == 200
    resp_json = resp.json()
    print("YoutubeGetDownloadList resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
    resp_code = resp_json["code"]
    if resp_code != 0:
        raise Exception(f"UpdatePodcastStatus failed, req:{req}, resp:{resp_json}")

if __name__ == "__main__":
    v = get_download_list()