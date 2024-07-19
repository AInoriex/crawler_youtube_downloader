# from utils.tool import load_cfg
# cfg = load_cfg("config.json")
# from config import Config
# config = Config()
# config.load_cfg("conf/config.json")
# cfg = config.cfg

from database import handler as dao

def main():
    # video_data = dao.Video(
    #     vid="VID12345",
    #     position=1,
    #     source_type=1,
    #     source_link="https://www.youtube.com/watch?v=12345",
    #     duration=100,
    #     cloud_type="obs",
    #     cloud_path="/cloud/path/to/video",
    #     language="en",
    #     status=0,
    #     lock=0,
    #     info='{"key": "value"}',
    # )
    # dao.create_video(video_data)
    # dao.get_video_by_vid("VID12345")

    vid, _, link, _ = dao.get_next_audio(
        f"WHERE status = 0 AND `lock` = 0 AND `language` = 'vt' AND `source_type` = 3"
    )

    # 更新vid信息

    print("[MAIN END]")

if __name__ == "__main__":
    main()