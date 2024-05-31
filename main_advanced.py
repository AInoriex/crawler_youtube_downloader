from youtubesearchpython.__future__ import VideosSearch
import asyncio
from utils.utime import random_sleep
from utils.file import save_json_to_file
from utils.logger import init_logger

logger = init_logger("ytb_search_async")
video_search = VideosSearch(query="english talk show", limit = 100, language="cn", region="US", timeout=5)
page_idx = 0

# 异步函数，用于延迟操作
async def get_next_search(search_obj:VideosSearch)->list:
    next_result = await search_obj.next()
    # print(result['result'])
    video_list = next_result['result']
    return video_list
 
# 主异步函数，用于调用上面的异步函数
async def main():
    logger.info("[MAIN START]")
    global page_idx
    global video_search

    while 1:
        page_idx += 1
        print(f"{page_idx} - current loop start")

        v_list = await get_next_search(video_search)  # 调用异步函数，并等待其完成
        logger.debug(f"{page_idx} - {v_list}")
        if len(v_list) <= 0:
            logger.warn("video list is null, main while loop exit.")
            break
        save_json_to_file(v_list)
        for video in v_list:
            print(f'{page_idx} - {video["title"]} - {video["link"]}')
        
        await asyncio.sleep(10)
        print(f"{page_idx} - current loop end")
    
    logger.info("[MAIN END]")
 
# 运行主异步函数
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())