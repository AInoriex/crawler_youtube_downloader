from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "https://www.youtube.com/watch?v=vSoKUOBpDCg"

proxies = {"http": "http://127.0.0.1:32110", "https": "https://127.0.0.1:32110"}

# yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies, use_po_token=True)
# yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies, allow_oauth_cache=True, use_oauth=True)
yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies, use_oauth=True, token_file=r"cache\pytubefix_token\tokens.json")
print("The title of video:", yt.title)

# ys = yt.streams.get_highest_resolution()
# ys.download(output_path="download")

# 1. 按照 itag 获取
# Itag details according to https://web.archive.org/web/20200516070826/https://gist.github.com/Marco01809/34d47c65b1d28829bb17c24c04a0096f
# ::return:: <stream> | None

# 1.1 Video
# yt.streams.get_by_itag(137) # 1080p
# yt.streams.get_by_itag(136) # 720p
# yt.streams.get_by_itag(135) # 480p
# yt.streams.get_by_itag(134) # 360p
# yt.streams.get_by_itag(133) # 240p
# yt.streams.get_by_itag(160) # 144p

# 1.2 Audio
ys = yt.streams.get_by_itag(140) # MP4 AAC	128 Kbps
# yt.streams.get_by_itag(251) # WebM Opus   ~160 Kbps	
# yt.streams.get_by_itag(250) # WebM Opus   ~70 Kbps	
# yt.streams.get_by_itag(249) # WebM Opus   ~50 Kbps	
download_filepath = ys.download(output_path="download", skip_existing=True, max_retries=3, timeout=10)
print(download_filepath)


# 2. 按照 filter 获取
# https://pytubefix.readthedocs.io/en/latest/api.html#stream-object
# video_stream_list = yt.streams.filter(only_video=True, resolution="1080p").itag_index
# video_stream_list = yt.streams.filter(only_video=True, resolution="720p").itag_index
# video_stream_list = yt.streams.filter(only_video=True, resolution="360p").itag_index
# for key in video_stream_list:
#     print(key, video_stream_list[key])

# audio_stream_list = yt.streams.filter(only_audio=True).itag_index
# for key in audio_stream_list:
#     print(key, audio_stream_list[key])



    