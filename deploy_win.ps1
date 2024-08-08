# git clone https://github.com/AInoriex/crawler_youtube_downloader.git
# crawler_youtube_downloader/deploy.ps1
# cd crawler_youtube_downloader

echo "ready to check env"
sleep 2
py -3 -V
ffmpeg -version

echo "ready to create venv"
sleep 2
py -3 -m venv .venv
.venv\Scripts\pip -V

echo "ready to install venv requirements"
sleep 2
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip

echo "ready to add google device code"
tree /F ./cache
mkdir -p ./cache/yt-dlp_1
mkdir -p ./cache/yt-dlp_2
tree /F ./cache
sleep 2
# .venv\Scripts\yt-dlp --username oauth2 --password '' --cache-dir ./cache/yt-dlp_1  --paths ./download/ https://www.youtube.com/watch?v=2mWbEZjqCYk
# .venv\Scripts\yt-dlp --username oauth2 --password '' --cache-dir ./cache/yt-dlp_2  --paths ./download/ https://www.youtube.com/watch?v=2mWbEZjqCYk
# tree /F ./cache

sleep 2
echo "scripts execute finished."