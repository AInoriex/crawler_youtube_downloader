from os import getenv, path, makedirs
import requests
from time import time, sleep
import json
from uuid import uuid4
from pprint import pprint
from utils.lark import alarm_lark_text
from utils.utime import get_now_time_string

OAUTH2_PATH = getenv("YTB_OAUTH2_PATH") if getenv("YTB_OAUTH2_PATH") else ""
''' YouTube账号缓存目录'''
print(f"youtube_account > 初始化账号cache路径：{OAUTH2_PATH}")

class YoutubeAccout:
    '''
    Youtube账号 Attributes:
        id (int): 账号id
        username (str): 用户名
        password (str): 密码
        verify_email (str): 验证邮箱
        login_name (str): 服务器名称
        status (int): 0: 初始化, 1: 可登陆, 2: 占用, -1: 失效
        token (str): 当前token值
        yt_dlp_oauth2_path (str): yt-dlp OAUTH2_PATH 路径
        yt_dlp_token_path (str): token_data.json 存放路径
    '''
    def __init__(self):
        self.id = 0 # 账号id
        self.username = "" # 用户名
        self.password = "" # 密码
        self.verify_email = "" # 验证邮箱
        self.login_name = getenv("SERVER_NAME")
        self.status = None # 0: 初始化, 1: 可登陆, 2: 占用, -1: 失效
        self.token = "" # 当前token值
        self.yt_dlp_oauth2_path = OAUTH2_PATH # yt-dlp OAUTH2_PATH 路径
        self.yt_dlp_token_path = "" # token_data.json 存放路径
        self.is_process:bool = False # 是否在处理换号

    def __del__(self):
        if self.status and self.status == 2:
            self.logout() 
        pass

    def print_account(self):
        '''
        打印当前youtube账号信息
        '''
        print("┌───────────── youtube account info ─────────────┐")
        print("youtube_account > id:", self.id)
        print("youtube_account > username:", self.username)
        print("youtube_account > password:", self.password)
        print("youtube_account > verify_email:", self.verify_email)
        print("youtube_account > login_name:", self.login_name)
        print("youtube_account > status:", self.status)
        print("youtube_account > token:", self.token)
        print("└─────────────  youtube account info ─────────────┘ ")
        return

    def get_account_info(self):
        '''
        获取当前youtube账号信息

        :return: dict
        '''
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "verify_email": self.verify_email,
            "login_name": self.login_name,
            "status": self.status,
            "token": self.token
        }

    def is_process(self):
        return self.is_process

    def get_new_account(self, retry:int=3):
        '''
        通过api获取一个可用的youtube账号
        @params retry: int, retry次数
        @return None
        '''
        url = getenv("CRAWLER_GET_ACCOUNT_API")
        if retry <= 0:
            print("youtube_account > [!] get_new_account FAILED, no more retry")
            return
        try:
            resp = requests.get(url=url, params={"sign": int(time())})
            print(f"youtube_account > [DEBUG] login_account response | status_code:{resp.status_code}, content:{str(resp.content, encoding='utf-8')}")
            assert resp.status_code == 200
            assert resp.json()["code"] == 0
            assert len(resp.json()["data"]) > 0
            self._format_crawler_account_response(resp.json()["data"])
            self.status = 2 # 账号设置为占用状态
            print("youtube_account > get_new_account succeed", resp.json())
            self.print_account()
        except Exception as e:
            print(f"youtube_account > [!] get_new_account ERROR, {e.__class__} | response:{str(resp.content, encoding='utf-8')}")

    def login(self, is_login=False, retry:int=3):
        '''账号登入
        @params is_login: bool, retry: int
        @return None
        '''
        url = getenv("CRAWLER_LOGIN_ACCOUNT_API")
        print(f"youtube_account > login_account {'SUCCESS' if is_login else 'FAIL'}, id:{self.id}, username:{self.username}, password:{self.password}")
        if retry <= 0:
            print("youtube_account > [!] login_account FAILED, no more retry")
            # TODO 告警
            return
        try:
            # RequestId     string `json:"request_id"`
            # Id            int64  `json:"id"`
            # IsLogin       bool   `json:"is_login"`
            # Token         string `json:"token"`
            # LastLoginUser string `json:"last_login_user"`
            reqbody = {
                "request_id": uuid4().hex,
                "id": self.id,
                "is_login": is_login,
                "token": json.dumps(self.token) if is_login else "",
                "last_login_user": self.login_name
            }
            print(f"youtube_account > [DEBUG] login_account request | reqbody:{reqbody}")
            resp = requests.post(url=url, params={"sign": int(time())}, json=reqbody)
            print(f"youtube_account > [DEBUG] login_account response | status_code:{resp.status_code}, content:{str(resp.content, encoding='utf-8')}")
            assert resp.status_code == 200
            assert resp.json()["code"] == 0
        except Exception as e:
            print("youtube_account > [!] login_account ERROR", reqbody, e)
            sleep(1)
            self.login(is_login=is_login, retry=retry-1)

    def logout(self, is_invalid:bool=False, comment:str="", retry:int=3):
        '''账号登出
        @params is_invalid: bool, comment: str, retry: int
        @return None
        '''
        url = getenv("CRAWLER_LOGOUT_ACCOUNT_API") # TODO
        if retry <= 0:
            print("youtube_account > [!] logout_account FAILED, no more retry")
            # TODO 告警
            return
        try:
            reqbody = {
                "request_id": uuid4().hex, 
                "id": self.id,
                "is_invalid": is_invalid,
                "comment": comment
            }
            # print(f"youtube_account > [DEBUG] logout_account request | reqbody:{reqbody}")
            resp = requests.post(url=url, params={"sign": int(time())}, json=reqbody)
            print(f"youtube_account > [DEBUG] logout_account response | status_code:{resp.status_code}, content:{str(resp.content, encoding='utf-8')}")
            assert resp.status_code == 200
            assert resp.json()["code"] == 0
        except Exception as e:
            print("youtube_account > [!] logout_account ERROR", e)
            sleep(1)
            self.logout(retry=retry-1)

    def _format_crawler_account_response(self, data:dict):
        '''根据Youtube账号API响应，格式化Youtube账号
        @params data: dict, API响应
        @return None
        '''
        try:
            data = data["result"]
            self.id = data["id"]
            self.username = data["username"]
            self.password = data["password"]
            self.verify_email = data["verify_email"]
            self.status = data["status"]
        except Exception as e:
            print("youtube_account > format_crawler_account_response failed", data, e)

    def account_auto_login(self, url:str, username:str, password:str, verify_email:str)->dict:
        '''自动登入账号
        @params url: str, API URL
        @params username: str, 账号用户名
        @params password: str, 账号密码
        @params verify_email: str, 验证邮箱
        @return str, token
        '''
        token = {}
        try:
            reqbody = {
                "username": username,
                "password": password,
                "recovery_email": verify_email
            }
            print(f"youtube_account > [DEBUG] account_auto_login request | url:{url} reqbody:{reqbody}")
            resp = requests.post(url=url,json=reqbody)
            print(f"youtube_account > [DEBUG] account_auto_login response | status_code:{resp.status_code}, content:{str(resp.content, encoding='utf-8')}")
            '''
            {
                "code": 200,
                "token": {
                    "yt-dlp_version": "2024.07.16",
                    "data": {
                        "access_token": "ya29.a0AcM612xN6nlG93dpWSOG1BMxererCwgjT1rFASqs6E-2sISQsBw7qJsKd1CyYj2FMHL081LUE5ORj3psOoB7ASeyQ2x5Mv0e5AISGNILZ7bUd8e5X5cF5v8hITJ2DeQn7Kj2Y_kY5HPwRZVt6mCNaAgPbSA1FjDgzZR4MMw-ByhP9OuFje6_aCgYKAWISARISFQHGX2MiiYtrrYHLkyOON6TJr-eGVA0187",
                        "expires": 1727977730.313632,
                        "refresh_token": "1//05BtEjsFRcEeSCgYIARAAGAUSNwF-L9IratYNDGrbD_PMuVOR2Jzgt-UmO5tSi4gi0Gl45nGFrhppDyFSazlQUrVCg774Vbnkx5I",
                        "token_type": "Bearer"
                    }
                }
            }
            '''
            assert resp.status_code == 200
            assert resp.json()["code"] == 200
            token = resp.json()["token"]
            print(f"youtube_account > account_auto_login {username} succeed")
            pprint(token)
        except Exception as e:
            # 登入失败
            print(f"youtube_account > account_auto_login failed with {resp}", e)
            # self.login_account(is_login=False)
        else:
            # 登入成功
            # self.login_account(is_login=True)
            pass
        finally:
            return token

    def save_token_to_file(self, token:dict, save_dir:str):
        """
        保存token到文件

        :param token: str, token
        :param save_dir: str, 保存目录
        :return: str, 保存成功的文件路径
        """
        try:
            # 判断路径存在，不存在创建
            if not path.exists(save_dir):
                makedirs(save_dir)
            token_path = path.join(save_dir, "token_data.json")
            with open(token_path, mode="w", encoding="utf8") as f:
                json.dump(token, f)
        except Exception as e:
            print(f"youtube_account > save_token_to_file failed", e)
        else:
            print(f"youtube_account > save_token_to_file succeed, {token_path}")
            return token_path

    def update_oauth2(self, token_path:str):
        """
        更新yt-dlp账号缓存路径

        :param token_path: str, 账号token_data.json文件路径
        :return: None
        """
        # token_path = r"./cache/yt_dlp_1727895706/youtube-oauth2\\token_data.json"

        # 判断path是否存在
        if not path.exists(token_path):
            print("youtube_account > 当前账号token文件不存在")
            return
        else:
            print(f"youtube_account > 当前账号token文件路径：{token_path}")

        # TODO 检验token文件格式

        # 提取yt-dlp需要的oauth2路径
        # 截取 */youtube-oauth2/token_data.json 前的路径
        # token_path = path.dirname(token_path)
        file_name_start = token_path.rfind('/youtube-oauth2')
        global OAUTH2_PATH
        OAUTH2_PATH = token_path[:file_name_start]
        self.yt_dlp_oauth2_path = OAUTH2_PATH
        print(f"youtube_account > 当前服务账号缓存更新成功：{OAUTH2_PATH}")
        return

    def youtube_login_handler(self)->int:
        """
       Youtube账号自动换号

        1. 获取可用账号
        2. 登录账号获取token
        3. token保存到文件
        4. 更新yt-dlp需要的oauth2路径

        :return: int, 0: success, -1: failed
        """
        try:
            self.is_process = True
            # 1. 获取可用账号
            self.get_new_account()
            if self.id <= 0 or self.username == "" or self.password == "" or self.verify_email == "":
                print("youtube_account > youtube_login_handler 获取新账号失败")
                return

            # 2. 登录账号获取token
            print("youtube_account > youtube_login_handler 正在自动登陆账号中，请稍后...")
            token = self.account_auto_login(
                url=getenv("CRAWLER_AUTO_LOGIN_API"),
                username=self.username,
                password=self.password,
                verify_email=self.verify_email,
            )
            # token = {"access_token": "ya29.a0AcM612zSm47CaujLJib3Igp59_vQk-r1CNg7ECZcn5daavXG7riav80NoSPMwPvN-B8gm7zE-NcC46IzRkP-qBqy2363WEvIYuwq1ViHbt7DynnmMXke75XwFtEPIGqPhJfpPhvHmVN96cqPmrZ-6soPOyyC6b0pJRs459QBcHTCZRg2LymXaCgYKARESARMSFQHGX2Mi9iA6jnCDRmJK8tbIiuD9Fw0187","expires": 1727970558.819872,"refresh_token": "1//050ihnwKTZaG0CgYIARAAGAUSNwF-L9IrejCMXEAqUKRWFhKL4e2enIXHqdTrg3Q8C0B8Pq4XzK4kH642DtHPPvanz0pgrg6Xv94","token_type": "Bearer"}
            if token == {}:
                print("youtube_account > youtube_login_handler 自动登陆账号失败, token为空")
                raise Exception("youtube_login_handler 自动登陆账号失败, token为空")
            self.token = token

            # 3. token保存到文件
            token_path = self.save_token_to_file(
                token=token,
                save_dir=f"./cache/yt_dlp_{int(time())}/youtube-oauth2"
            )
            if token_path == "":
                print("youtube_account > youtube_login_handler 保存token失败")
                raise Exception("youtube_login_handler 保存token失败")
            self.yt_dlp_token_path = token_path

            # 4. 更新yt-dlp需要的oauth2路径
            self.update_oauth2(token_path=token_path)

            # 5. 更新状态
            self.login(is_login=True)
        except Exception as e:
            print("youtube_account > [!] youtube_login_handler ERROR", e.__class__)
            self.login(is_login=False)
            # 告警
            notice_text = f"[Youtube Crawler ACCOUNT | ERROR] 自动换号失败. \
                \n\t登入方: {self.login_name} \
                \n\t账密: {self.id} | {self.username} {self.password} \
                \n\tOAUTH2_PATH: {OAUTH2_PATH} \
                \n\tERROR: {e} \
                \n\t告警时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
            raise e
        else:
            # 告警
            notice_text = f"[Youtube Crawler ACCOUNT | INFO] 自动换号成功. \
                \n\t登入方: {self.login_name} \
                \n\t账密: {self.id} | {self.username} {self.password} \
                \n\tOAUTH2_PATH: {OAUTH2_PATH} \
                \n\tToken Path: {self.yt_dlp_token_path} \
                \n\tToken Content: {self.token} \
                \n\t告警时间: {get_now_time_string()}"
            alarm_lark_text(webhook=getenv("LARK_ERROR_WEBHOOK"), text=notice_text)
        finally:
            self.is_process = False

    def get_token_from_file(self, token_path:str)->dict:
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


if __name__ == "__main__":
    ac = YoutubeAccout()
    # ac.youtube_login_handler()

    # token = ac.account_auto_login(
    #     url=getenv("CRAWLER_AUTO_LOGIN_API"),
    #     username="rasolelonsdale@gmail.com",
    #     password="72nwt1czs",
    #     verify_email="maillouxulwellinghg789@yahoo.com",
    # )

    # ac.update_oauth2(
    #     token_path=r"./cache/yt_dlp_1727895706/youtube-oauth2\\token_data.json"
    # )

    # url = getenv("CRAWLER_LOGIN_ACCOUNT_API")
    # is_login = True
    # data = {
    #     'request_id': '1b768778ec27407dbc7a0046d0655731', 
    #     'id': 2, 
    #     'is_login': True, 
    #     'token': {
    #         'yt-dlp_version': '2024.07.16', 
    #         'data': {}
    #     },
    # }
    # reqbody = {
    #     "request_id": uuid4().hex,
    #     "id": 2,
    #     "is_login": is_login,

    #     "token": json.dumps(data),

    #     "last_login_user": "test"
    # }
    # print(f"youtube_account > [DEBUG] login_account request | reqbody:{reqbody}")
    # resp = requests.post(url=url, params={"sign": int(time())}, json=reqbody)
    # print(f"youtube_account > [DEBUG] login_account response | status_code:{resp.status_code}, content:{str(resp.content, encoding='utf-8')}")