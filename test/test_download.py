import urllib.request as request
from uuid import uuid4
import time
from random import randint
# from utils.config import config
import yaml
from utils.context import Context

def load_config(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config
config = load_config("config.yaml")

# youtube_url = r"https://www.youtube.com/watch?v=jk475BA62UU&list=UUy5Y_wZdTy898iv1EL_O8eg&index=2368&pp=iAQB"
# youtube_vid = get_youtube_vid(youtube_url)
video_url = r"https://rr3---sn-uxax4vopj5qx-cxgl.googlevideo.com/videoplayback?expire=1733841771&ei=C_9XZ8-bHZGz6dsPiZ-kUA&ip=176.6.145.37&id=o-ADxc-01POacK8N6xnbVwO0P9wnOnziXu0BWJZ-4Pl6k7&itag=18&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1733820171%2C&mh=jN&mm=31%2C29&mn=sn-uxax4vopj5qx-cxgl%2Csn-4g5e6nzl&ms=au%2Crdu&mv=m&mvi=3&pl=17&rms=au%2Cau&initcwndbps=717500&bui=AQn3pFSmbTfoAXctpbUVA03t0xvBnye7urq1PtZHsp9iQYGe58zRYmiFsQjds1lGSRpCKSsc50x09-Xr&spc=qtApAZDmo4__6s-HQrkyeUyrNzZeICXUpnCCzUclQ6mJPPTQVejP&vprv=1&svpuc=1&mime=video%2Fmp4&ns=_iTHafltopZ5KY-RQN-lENQQ&rqh=1&cnr=14&ratebypass=yes&dur=77.902&lmt=1716660133244107&mt=1733819809&fvip=4&fexp=51326932%2C51335594%2C51347747%2C51355912&c=WEB&sefc=1&txp=8218224&n=dhbGzOdZYyw_Tw&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Ccnr%2Cratebypass%2Cdur%2Clmt&sig=AJfQdSswRQIhAK1-StKlhv_QorQLw1wZRQmEPtWOnaH6mm4FaOR8aQ-3AiBLaNisjum3FxvcGNqRtFZtRyc81xV7WPxjaK8e5XXP4w%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=AGluJ3MwRQIgbDZJ79e7Lze31F-G2cw7fb7SXzdYGxHn_k27kw-p9JACIQC3yHFWWHtyj0SgJNs0qu6uPaSNj_Qb2KNfUEMGGSKyXA%3D%3D"
local_filename = f'./download/youtube/{str(uuid4())}.mp4'
proxyip = config['HTTP_PROXY']
proxies={
    'http': proxyip,
    'https': proxyip,
}

ctx = Context()
ctx.set_ctx('video_url', video_url)
ctx.set_ctx('local_filename', local_filename)
ctx.set_ctx('http_proxy', proxyip)

def get_youtube_vid(url:str):
    """ 解析youtube视频id """
    import re
    from uuid import uuid4
    default = uuid4()
    try:
        # 使用正则表达式匹配v参数
        video_id_match = re.search(r"v=([^&#]+)", url)
        if video_id_match:
            video_id = video_id_match.group(1)
            return video_id
        else:
            raise ValueError("get_youtube_vid re.search failed")
    except Exception as e:
        print(f"get_youtube_vid > error, {e}")
        return default

def download_file(ctx:Context, url:str, local_filename:str, proxies=proxies, retry=3):
    """
    使用代理服务器从url处下载文件到本地的local_filename

    :param url: 要下载的文件的url
    :param local_filename: 保存到本地的文件名
    :return: None
    """
    ctx.set_ctx('error', '')
    ctx.set_ctx('retry_left', retry)
    # 可选的reporthook函数，用于显示下载进度
    def reporthook(block_num, block_size, total_size):
        if total_size != -1:
            file_size = f"{total_size/1048576:.2f}MB"
            if not ctx.has_ctx('file_size'):
                ctx.set_ctx('file_size', file_size)
            print(f"\r文件大小: {file_size} | 下载进度：{block_num*block_size/total_size*100:.2f}%", end='')

    print(f"download_file > 下载参数 From: {url} | To: {local_filename}, retry:{retry}")
    time_st = time.time()
    try:
        # create the object, assign it to a variable
        proxy_handler = request.ProxyHandler(proxies)
        # proxy_handler = request.ProxyHandler()

        # construct a new opener using your proxy settings
        opener = request.build_opener(proxy_handler)

        # 定义请求头
        headers = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0')
        ]
        opener.addheaders = headers

        # install the openen on the module-level
        request.install_opener(opener)

        request.urlretrieve(url, local_filename, reporthook)
    except Exception as e:
        print(f"\ndownload_file > 下载文件时发生错误：{e}")
        if retry > 0:
            time.sleep(randint(3,5))
            download_file(ctx=ctx, url=url, local_filename=local_filename, retry=retry-1)
        else:
            ctx.set_ctx('error', e)
            raise e
    else:
        print(f"\ndownload_file > 文件已下载到：{local_filename}")
        spend_time = round(time.time()-time_st, 2)
        print(f"下载花费时间：{spend_time}秒")
        ctx.set_ctx('spend_time(second)', spend_time)

if __name__ == "__main__":
    # # 解析1
    # from tubedown import extract_download_url
    # # url_info = extract_download_url(youtube_url=youtube_url, proxies={})
    # url_info = extract_download_url(youtube_url=youtube_url, proxies=proxies)
    # # 提取链接
    # video_url = url_info["video_info"]["url"]
    
    # 解析2
    # from test_rapid_api import get_video_info_v2
    # vinfo = get_video_info_v2(video_id=youtube_vid)
    # video_url = vinfo.get('url')
    # print(f"解析花费时间:{round(time.time()-time_1, 2)}秒")
    
    # 调用函数下载文件
    download_file(ctx, video_url, local_filename)
    
    # 结果输出
    ctx.write_to_file()