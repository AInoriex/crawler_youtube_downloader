import asyncio
import base64
import binascii
import json
import math
import os
import re
import time
import traceback

import aiofiles
import aiohttp
import requests
from Crypto.Cipher import AES
import colorama


all_cate = {
    "音乐": 2,
    "有声书": 3,
    "娱乐": 4,
    "外语": 5,
    "儿童": 6,
    "商业财经": 8,
    "历史": 9,
    "相声评书": 12,
    "个人成长": 13,
    "广播剧": 15,
    "有声图书": 1001,
    "人文国学": 1002,
    "热点": 1005,
    "生活": 1006,
    "新红色频道": 1054,
    "悬疑": 1061,
    "健康": 1062,
    "汽车": 1065,
}
swapped_all_cate = {v: k for k, v in all_cate.items()}


class Ximalaya:
    def __init__(self):
        self.default_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1660.14"
        }

    def get_download_link(self, sound_id, headers):
        url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
        params = {"device": "web", "trackId": sound_id, "trackQualityLevel": 2}

        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()

        if not data["trackInfo"]["isAuthorized"]:
            return 0

        sound_name = data["trackInfo"]["title"]
        encrypted_url_list = data["trackInfo"]["playUrlList"]

        sound_info = {"name": sound_name, 0: "", 1: "", 2: ""}
        for encrypted_url in encrypted_url_list:
            if encrypted_url["type"] == "M4A_128":
                sound_info[2] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_64":
                sound_info[1] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_32":
                sound_info[0] = self.decrypt_url(encrypted_url["url"])

        return sound_info

    def get_track_list(self, album_id):
        url = "https://www.ximalaya.com/revision/album/v1/getTracksList"
        params = {"albumId": album_id, "pageNum": 1, "pageSize": 100}

        response = requests.get(
            url, headers=self.default_headers, params=params, timeout=15
        )

        data = response.json()

        pages = math.ceil(data["data"]["trackTotalCount"] / 100)

        sounds = []
        for page in range(1, pages + 1):
            params = {"albumId": album_id, "pageNum": page, "pageSize": 100}

            response = requests.get(
                url, headers=self.default_headers, params=params, timeout=30
            )

            sounds += data["data"]["tracks"]

        album_name = sounds[0]["albumTitle"]

        return album_name, sounds

    async def async_get_download_link(self, sound_id, session, headers):
        url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
        params = {"device": "web", "trackId": sound_id, "trackQualityLevel": 2}

        async with session.get(
            url, headers=headers, params=params, timeout=60
        ) as response:
            response_json = json.loads(await response.text())
            sound_name = response_json["trackInfo"]["title"]
            encrypted_url_list = response_json["trackInfo"]["playUrlList"]

        if not response_json["trackInfo"]["isAuthorized"]:
            return 0

        sound_info = {
            "name": sound_name,
            0: "",
            1: "",
            2: "",
            "trackId": 0,
            "title": 0,
            "categoryId": 0,
            "intro": 0,
            "uid": 0,
            "nickname": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "duration": 0,
            "albumId": 0,
        }

        for key in [
            "trackId",
            "title",
            "categoryId",
            "intro",
            "uid",
            "nickname",
            "likes",
            "comments",
            "shares",
            "duration",
        ]:
            try:
                sound_info[key] = response_json["trackInfo"][key]
            except:
                sound_info[key] = None

        for key in ["albumId"]:
            try:
                sound_info[key] = str(response_json["albumInfo"][key])
            except:
                sound_info[key] = None

        sound_info["trackId"] = sound_id

        # sound_info['trackId'] = '_'.join(['xmly0000000',str(sound_info['albumId']), str(sound_info['trackId'])])

        for encrypted_url in encrypted_url_list:
            if encrypted_url["type"] == "M4A_128":
                sound_info[2] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_64":
                sound_info[1] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_32":
                sound_info[0] = self.decrypt_url(encrypted_url["url"])

        return sound_info

    def replace_invalid_chars(self, name):
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        for char in invalid_chars:
            if char in name:
                name = name.replace(char, " ")
        return name

    def download_sound(self, sound_name, sound_url, path):
        retries = 3
        sound_name = self.replace_invalid_chars(sound_name)
        if "?" in sound_url:
            type = sound_url.split("?")[0][-3:]
        else:
            type = sound_url[-3:]
        path = os.path.join(path, "audio")
        os.makedirs(path, exist_ok=True)
        save_path = os.path.join(path, sound_name + "." + type)
        if os.path.exists(save_path):
            print(f"{sound_name} exist")
            return save_path
        while retries > 0:
            try:
                print(f"Start downloading {sound_name}")
                response = requests.get(
                    sound_url, headers=self.default_headers, timeout=60
                )
                break
            except Exception as e:
                print(f"{sound_name} > {4 - retries} times download fail")
                print(traceback.format_exc())
                retries -= 1
        if retries == 0:
            print(colorama.Fore.RED + f"{sound_name} download fail")
            return False
        sound_file = response.content
        with open(save_path, mode="wb") as f:
            f.write(sound_file)
        print(f"{sound_name} download success")
        return save_path

    async def async_get_sound(
        self, sound_info, sound_name, sound_url, album_name, session, path
    ):
        # TODO: Test this function
        print(f"Start downloading {sound_name}")
        # if num is None:
        #     sound_name = self.replace_invalid_chars(sound_name)
        # else:
        #     sound_name = f"{num}-{sound_name}"
        #     sound_name = self.replace_invalid_chars(sound_name)
        if "?" in sound_url:
            type = sound_url.split("?")[0][-3:]
        else:
            type = sound_url[-3:]
        # album_name = self.replace_invalid_chars(album_name)
        # print(album_name)

        audio_path = os.path.join(path, "audio")
        info_path = os.path.join(path, "info")
        os.makedirs(audio_path, exist_ok=True)
        os.makedirs(info_path, exist_ok=True)

        try:
            with open(
                f"{info_path}/{album_name}_{sound_name}.json", "w", encoding="utf8"
            ) as f:
                new_dict = dict(
                    [
                        (key2, sound_info[key1])
                        for key1, key2 in [
                            ("trackId", "id"),
                            ("title", "title"),
                            ("full_url", "full_url"),
                            ("nickname", "author"),
                            ("duration", "duration"),
                            ("categoryId", "categories"),
                        ]
                    ]
                )
                new_dict["tag"] = [sound_info["intro"]]
                new_dict["view_count"] = None
                new_dict["comment_count"] = sound_info["comments"]
                new_dict["follower_count"] = None
                new_dict["upload_date"] = None

                new_dict["categories"] = swapped_all_cate[new_dict["categories"]]

                json.dump(dict(**new_dict), f, indent=4, ensure_ascii=False)
        except:
            return False

        file_path = f"{audio_path}/{album_name}_{sound_name}.{type}"

        if not os.path.exists(file_path):
            try:
                async with session.get(
                    sound_url, headers=self.default_headers, timeout=120
                ) as response:
                    async with aiofiles.open(file_path, mode="wb") as f:
                        await f.write(await response.content.read())
                print(f"{sound_name} download success")
            except Exception as e:
                print(f"{sound_name} > download fail")
                print(traceback.format_exc())
                if os.path.exists(file_path):
                    os.remove(file_path)
                return False

        return file_path

    async def get_selected_sounds(
        self, sounds, album_name, headers, quality, number, path
    ):
        tasks = []
        session = aiohttp.ClientSession()
        digits = len(str(len(sounds)))
        for sound in sounds:
            sound_id = sound["trackId"]
            tasks.append(
                asyncio.create_task(
                    self.async_get_download_link(sound_id, session, headers)
                )
            )
        sounds_info = await asyncio.gather(*tasks)
        tasks = []
        if number:
            num = 1
            tt = 0
            for sound_info in sounds_info:
                if sound_info is False or sound_info == 0:
                    continue
                tt += float(sound_info["duration"])
                num_ = str(num).zfill(digits)
                if quality == 2 and sound_info[2] == "":
                    quality = 1
                sound_info["full_url"] = "https://www.ximalaya.com/sound/" + str(
                    sound_info["trackId"]
                )
                tasks.append(
                    asyncio.create_task(
                        self.async_get_sound(
                            sound_info,
                            "_".join(
                                ["xmly00000", album_name, str(sound_info["trackId"])]
                            ),
                            sound_info[quality],
                            album_name,
                            session,
                            path,
                        )
                    )
                )
                num += 1
        else:
            for sound_info in sounds_info:
                if sound_info is False or sound_info == 0:
                    continue
                if quality == 2 and sound_info[2] == "":
                    quality = 1
                tasks.append(
                    asyncio.create_task(
                        self.async_get_sound(
                            sound_info["name"],
                            sound_info[quality],
                            album_name,
                            session,
                            path,
                        )
                    )
                )

        results = await asyncio.gather(*tasks)

        success_downloads = [result for result in results if result]
        failed_downloads = [result for result in results if result is False]

        print("failed_downloads", failed_downloads)

        print("All sounds downloaded!")

        await session.close()

        return success_downloads

    def decrypt_url(self, ciphertext):
        key = binascii.unhexlify("aaad3e4fd540b0f79dca95606e72bf93")
        ciphertext = base64.urlsafe_b64decode(
            ciphertext + "=" * (4 - len(ciphertext) % 4)
        )
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = cipher.decrypt(ciphertext)
        plaintext = re.sub(r"[^\x20-\x7E]", "", plaintext.decode("utf-8"))
        return plaintext

    def judge_album(self, album_id, headers):
        url = "https://www.ximalaya.com/revision/album/v1/simple"
        params = {"albumId": album_id}

        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()

        if not data["data"]["albumPageMainInfo"]["isPaid"]:
            return 0  # free
        elif data["data"]["albumPageMainInfo"]["hasBuy"]:
            return 1  # paid
        else:
            return 2  # vip

    def get_username(self, cookie):
        url = "https://www.ximalaya.com/revision/my/getCurrentUserInfo"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1660.14",
            "cookie": cookie,
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()
        except Exception as e:
            print("Cannot get Ximalaya user data!")
            print(traceback.format_exc())
        if data["ret"] == 200:
            return data["data"]["userName"]
        else:
            return False


ximalaya = Ximalaya()
loop = asyncio.get_event_loop()


def download(url, file_id, save_path, is_xmcdn=False):
    if is_xmcdn:
        sound_name = url.split("/")[-1].split(".")[0]
        return ximalaya.download_sound(sound_name, url, save_path)
    if "album" in url:
        return download_by_playlist(url, save_path)

    return download_by_url(url, file_id, save_path)


def download_by_url(link, file_id, path):
    # link: single ximalaya audio link
    # path: download path
    try:
        sound_id = re.search(r"sound/(?P<sound_id>\d+)", link).group("sound_id")
    except Exception:
        print("Wrong audio link format", link)
        return
    sound_info = ximalaya.get_download_link(sound_id, ximalaya.default_headers)
    if sound_info == 0:
        print(f"VIP audio {sound_id} not paid, skip downloading")
        return
    sound_name = sound_info["name"]
    if file_id is not None:
        sound_name = file_id
    sound_url = sound_info[2] if sound_info[2] else sound_info[1]
    save_path = ximalaya.download_sound(sound_name, sound_url, path)
    return save_path


def get_id(url):
    url = url.strip()
    if "ximalaya.com" in url:
        try:
            sound_id = re.search(r"sound/(?P<sound_id>\d+)", url).group("sound_id")
            return sound_id
        except Exception:
            pass
        try:
            album_id = re.search(r"album/(?P<album_id>\d+)", url).group("album_id")
            return album_id
        except Exception:
            return False
    try:
        album_id = int(url)
        return album_id
    except ValueError:
        return False


def download_by_playlist(playlist, path):
    # playlist: ximalaya playlist link
    # path: download path
    album_id = get_id(playlist)
    album_name, sounds = ximalaya.get_track_list(album_id)
    if not sounds:
        return
    album_type = ximalaya.judge_album(album_id, ximalaya.default_headers)
    if album_type == 0:
        print(f"Free - {album_id} - {album_name} - {len(sounds)} audios")
    elif album_type == 1:
        print(f"Paid {album_id} - {album_name} - all {len(sounds)} audios")
    elif album_type == 2:
        print(f"VIP {album_id} - {album_name} not paid, skip downloading")
        return

    album_name = str(album_id)  # instead of album_name

    result = loop.run_until_complete(
        ximalaya.get_selected_sounds(
            sounds, album_name, ximalaya.default_headers, 2, True, path
        )
    )
    return result


if __name__ == "__main__":
    cookie = os.getenv("XIMA_COOKIE")
    path = os.getenv("XIMA_PATH")
    if not cookie:
        username = False
    else:
        username = ximalaya.get_username(cookie)

    if path:
        os.makedirs(path, exist_ok=True)
    print(f"Download path: {path}")

    response = requests.get(
        f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}?device=web&trackId=188017958&trackQualityLevel=1",
        headers=ximalaya.default_headers,
    )
    data = response.json()

    if data["ret"] == 927 and not username:
        print(
            "Ximalaya not support oversea anonymous user to download vip audio, please config your cookie first."
        )
        exit(0)

    if username:
        print(
            f"Logged in: {username}, cookie will be used to download vip audio, please make sure the cookie is valid."
        )
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1660.14",
            "cookie": cookie,
        }
        logined = True
    else:
        print("Not logged in, only free audio can be downloaded.")
        headers = ximalaya.default_headers
        logined = False

    while True:
        print("Enter file path to download album list:")
        input_album_list = input()
        results = []
        for input_album in open(input_album_list, "r").readlines():
            try:
                r = download_by_playlist(input_album, path)
                results.extend(r)
            except:
                pass

        print("All albums downloaded!")
        print("Results", results)
