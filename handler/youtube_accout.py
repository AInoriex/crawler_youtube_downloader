from os import getenv, path, makedirs
import requests
from time import time
import json

OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
print(f"youtube_account > 初始化账号cache路径：{OAUTH2_PATH}")

class YoutubeAccout:
    def __init__(self):
        self.token = ""
        pass
    def get_new_account(retry:3):
        api = "https://magicmir.52ttyuyin.com/crawler_api/get_youtube_available_account"
        if retry <= 0:
            return

        try:
            pass
        except Exception as e:
            print(e)
            update_account(retry=retry-1)


    def update_account(retry:3):
        api = "https://magicmir.52ttyuyin.com/crawler_api/youtube_account_login"
        if retry <= 0:
            return
        api = ""
        try:
            pass
        except Exception as e:
            print(e)
            update_account(retry=retry-1)


def account_auto_login(api:str, username:str, password:str, verify_email:str):
    token = ""
    try:
        resp = requests.post(
            url=api,
            data={
                "username": username,
                "password": password,
                "verify_email": verify_email
            }
        )

        assert resp.status_code == 200
        assert resp.json()["code"] == 0

        token = resp.json()["token"]
        print("youtube_account > account_auto_login succeed {}", token)
    except Exception as e:
        print(f"youtube_account > account_auto_login failed with {resp}", e)
    else:
        return token

def save_token_to_file(token:str, save_dir:str):
    """
    保存token到文件

    :param token: str, token
    :param save_dir: str, 保存目录
    :return: str, 保存成功的文件路径
    """
    token = '{"yt-dlp_version": "2024.07.16", "data": {"access_token": "ya29.a0AcM612zmzWAAl1TNm_FOqcdI31jxdO4IVMn-PCNl5TN7GjB1kAjzza_iqFam0Gxb7EJZ-ickeAc7E1ntk1M_bhhW-RkoXp0IHRyg7Z2awa8MXwo9-jhdLUDzt7FYX1JOA_8xn3afP5YJ99fRiTqaGKn6cBWbiDtriBj7It5vXyiFcu7Clv-HaCgYKAToSARESFQHGX2MiIR_CTn0yPG6CIWDV5cjBAw0187", "expires": 1727853123.624623, "refresh_token": "1//0eivEhDcDJ8ueCgYIARAAGA4SNwF-L9IrCJsaLL-xGebNF6ng_a6MD_-jg_v_rRN2KDVNceU1MsbsUS7IxlV_cu7wFMxRUMii8Y0", "token_type": "Bearer"}}'
    try:
        # 判断路径存在，不存在创建
        if not path.exists(save_dir):
            makedirs(save_dir)
        token_path = path.join(save_dir, "token_data.json")
        with open(token_path, "w", encoding="utf8") as f:
            f.write(token)
    except Exception as e:
        print(f"youtube_account > save_token_to_file failed", e)
    else:
        print(f"youtube_account > save_token_to_file succeed, {token_path}")
        return token_path

def get_token_from_file(token_path:str)->dict:
    """
    从文件中获取token

    :param token_path: str, token文件路径
    :return: dict, token数据
    """
    ret = {}
    try:
        if not path.exists(token_path):
            print(f"youtube_account > get_token_from_file {token_path}文件不存在")
            return ret
        with open(token_path, "r", encoding="utf8") as f:
            ret = json.load(f)
    except Exception as e:
        print(f"youtube_account > get_token_from_file failed", e)
    else:
        print(f"youtube_account > get_token_from_file succeed, {ret}")
    finally:
        return ret



def update_oauth2(token_path:str):
    """
    更新yt-dlp账号缓存路径

    :param token_path: str, 账号token_data.json文件路径
    :return: None
    """
    # token_path = r"G:\QuWan\crawler\crawler_youtube_downloader\cache\yt-dlp_1\youtube-oauth2\token_data.json"

    # 判断path是否存在
    if not path.exists(token_path):
        print("youtube_account > 当前账号token文件不存在")
        return
    else:
        print(f"youtube_account > 当前账号token文件路径：{token_path}")

    # TODO 检验token文件格式

    # 提取yt-dlp需要的oauth2路径
    # 截取 */youtube-oauth2/token_data.json 前的路径
    token_path = path.dirname(token_path)
    file_name_start = token_path.rfind('\\') + 1
    OAUTH2_PATH = token_path[:file_name_start - 1]

    print(f"youtube_account > 当前账号缓存更新成功：{OAUTH2_PATH}")
    return


if __name__ == "__main__":
    # account_auto_login()
    token_path = save_token_to_file(
        token="",
        save_dir=f"./cache/yt_dlp_{int(time())}/youtube-oauth2"
    )
    update_oauth2(token_path=token_path)