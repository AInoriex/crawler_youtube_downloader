import requests
from time import sleep
from random import choice, randint

# 第三方解析youtube视频地址 2
def get_video_info_v2(video_id, geo='US', retry=3):
    # Refer     https://rapidapi.com/ytjar/api/ytstream-download-youtube-videos
    # Pricing   https://rapidapi.com/ytjar/api/ytstream-download-youtube-videos/pricing
    # Calls Limit   200 / Day
    # Rate Limit    1000 requests / hour
    try:
        url = f"https://yt-api.p.rapidapi.com/dl?id={video_id}&cgeo={geo}"
        # Set up the headers with the RapidAPI key
        headers = {
            'x-rapidapi-host': 'yt-api.p.rapidapi.com',
            'x-rapidapi-key': 'cc0f530252mshcd81b9c614428aep140232jsn4cb1d6dfebb3',
            'accept': 'application/json'
        }

        # Send the request
        response = requests.get(url, headers=headers)
        # Check if the request was successful
        if response.status_code != 200:
            raise ValueError(f"get_video_info_v2 request error, status_code:{response.status_code}")

        # Parse the JSON response
        resp = response.json()
        if resp.get('status') != 'OK':
            raise ValueError(f"get_video_info_v2 request error, {response.status_code} | {resp.get('status')}")
        # pprint(resp)

        # 提取视频
        highest_height = 0
        video_info = {}
        formats = resp.get("formats", [])
        for resolution in ["1080p", "720p", "480p", "360p", "240p", "144p"]:
            for fmt in formats:
                if resolution in fmt.get('qualityLabel', "") and fmt.get('url', "").startswith("https"):
                    height_value = int(fmt.get("height", 0))
                    if height_value > highest_height:
                        video_info = fmt
                        highest_height = height_value
        if not video_info:
            raise ValueError("get_video_info_v2 get empty response data info")
        return video_info
    except Exception as e:
        print(f"Error occurred while processing get_video_info_v2: {e}")
        if retry > 0:
            sleep(randint(5,10))
            get_video_info_v2(video_id=video_id, geo=geo, retry=retry-1)
        else:
            raise e