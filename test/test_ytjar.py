# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

def ytjar_test():
    from handler.yt_api import ytapi_handler
    print("ytjar_test start")
    # result = ytapi_handler(video_id="hWpYvHYVWsQ", save_path=r"download/ytjar")
    result = ytapi_handler(video_id="BiqbRQkVwVQ", save_path=r"download/ytjar")
    print("ytjar_test result:", result)

if __name__ == "__main__":
    ytjar_test()