from dotenv import load_dotenv
load_dotenv()

from database import handler as dao
from database import youtube_api
from utils import obs
from handler import youtube

def main():
    print("[MAIN START]")

    # # Database Handler
    # DatabaseCURDTest()

    # # Database Apis
    # DatabaseApisTest()
   
    # Cloud Storage Upload
    # ObsUploadTest()

    # Func Test
    youtube.is_touch_fish_time()

    print("[MAIN END]")
    exit()

def DatabaseCURDTest():
    # Create
    video_data = dao.Video(
    vid="VID12345",
    position=1,
    source_type=1,
    source_link="https://www.youtube.com/watch?v=12345",
    duration=100,
    cloud_type="obs",
    cloud_path="/cloud/path/to/video",
    language="en",
    status=0,
    lock=0,
    info='{"key": "value"}',
    )
    dao.create_video(video_data)
    dao.get_video_by_vid("VID12345")

    # Query
    id, _, link, _ = dao.get_next_audio(
        f"WHERE status = 0 AND `lock` = 0 AND `language` = 'vt' AND `source_type` = 3"
    )

    # Update
    dao.uploaded_download(id=id, cloud_type="obs", cloud_path=link)

def DatabaseApisTest():
    v = youtube_api.get_video_for_download(
        query_id=0,
        query_source_type=0
    )
    if v is None:
        print("Nothing to get")
        return
    print(v)

    v.cloud_type = 2
    v.cloud_path = "www.google.com"
    youtube_api.update_video_record(v)

def ObsUploadTest():
    from_path = r"/path/to/file.txt"
    to_path = r"/data/debug/xxx.txt"
    # obs.upload_file(from_path, to_path)
    obs.upload_file_v2(from_path, to_path)

if __name__ == "__main__":
    main()
