from handler.pytubefix import *
from database.crawler_download_info import Video


video = Video (
    vid="ytb_bO-O74L-5A4",
    position=1,
    source_type=1,
    source_link="https://www.youtube.com/watch?v=bO-O74L-5A4",
    duration=100,
    cloud_type=2,
    cloud_path="/cloud/path/to/video",
    language="test",
    status=0,
    lock=0,
    info='{"key": "test"}',
)
# pytubefix_login_handler()
download_path = pytubefix_audio_handler(video, save_path="download/test")
print(download_path)
