from youtubesearchpython import VideosSearch
from utils.file import save_json_to_file
import json

# videosSearch = VideosSearch(query="english talk show", limit = 1000, language="en", region="US")
videosSearch = VideosSearch(query="english talk show", limit = 2, language="cn", region="US")
print("content:", videosSearch.result())
print("type:", videosSearch.result())

# json_videoSearch = json.loads(videosSearch.result())
# print("content:", json_videoSearch)
# print("type:", json_videoSearch)

save_json_to_file(videosSearch.result())

print("[END]")