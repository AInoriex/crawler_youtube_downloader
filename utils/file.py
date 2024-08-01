# -*- coding: UTF8 -*-
# from utils.tool import load_cfg
# from config import Config
# config = Config()
# config.load_cfg("conf/config.json")
# config = Config()
# cfg = config.cfg

import os
import time
import json
import requests

def get_file_size(filePath):
    ''' 获取文件大小(MB) '''
    fsize = os.path.getsize(filePath)
    return fsize/float(1024*1024)

def save_json_to_file(data_dict:dict)->bool:
    ''' 保存json文件到本地 '''
    # output_path = cfg["common"]["tmp_folder_path"]
    output_path = os.getenv("TMP_FOLDER_PATH")
    os.makedirs(output_path, exist_ok=True)
    log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    try:
        with open(f"{output_path}/{log_time}.json", "w", encoding="utf8") as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("[ERROR] save_json_to_file failed", e)
        return False
    else:
        return True

async def save_json_to_file(data:any)->bool:
    ''' 保存json文件到本地 '''
    # output_path = cfg["common"]["tmp_folder_path"]
    output_path = os.getenv("TMP_FOLDER_PATH")
    os.makedirs(output_path, exist_ok=True)
    log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    try:
        with open(f"{output_path}/{log_time}.json", "w", encoding="utf8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("[ERROR] save_json_to_file failed", e)
        return False
    else:
        return True

# def save_any_to_file()->bool:
#     ''' 保存任意数据到本地 '''
#     output_path = cfg["common"]["tmp_folder_path"]
#     os.makedirs(output_path, exist_ok=True)
#     log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     try:
#         with open(f"{output_path}/{log_time}_raw.txt", "w", encoding="utf8") as f:
#             json.dump(data_dict, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         print("[ERROR] save_json_to_file failed", e)
#         return False
#     else:
#         return True

def dump_info(info_dict, out_file):
    ''' 保存json文件到本地
    @info_dict: 待打包服务
    @out_file: 保存路径
    '''
    with open(out_file, "w", encoding="utf8") as out:
        json.dump(info_dict, out, indent=4, ensure_ascii=False)

def download_url_resource_local(url:str, local_path:str)->bool:
    ''' 下载url资源到本地 '''
    base = os.path.dirname(local_path)
    os.makedirs(base, exist_ok=True)

    if url == "" or not url.startswith("http"):
        print(f"[Warn] url无效，下载跳过; url:{url}")
        return False
    if os.path.exists(local_path):
        print(f"[Warn] 该路径下{local_path}文件存在，下载跳过")
        return True

    headers={}
    proxies={}
    try:
        resp = requests.get(url, headers=headers,proxies=proxies,timeout=(5,20),verify=False)
        if not resp.status_code == 200:
            print(f"download_url_resource_local get url failed. url:{url}")
            return False
        with open(local_path ,mode="wb") as f:
            f.write(resp.content)
    except Exception as e:
        print(f"download_url_resource_local unknown error:{e}")
        return False
    else:
        print(f"download_url_resource_local download succeed. file:{local_path}")
        return True

if __name__ == "__main__":
    url = "https://mcdn.podbean.com/mf/web/3qznfg92me6zs3m4/04-18-Molly-promo-final.mp3"
    save_path = os.path.join(".", "download", "test", "04-18-Molly-promo-final.mp3")
    succ = download_url_resource_local(url=url, local_path=save_path)
    print(f"flag:{succ}")