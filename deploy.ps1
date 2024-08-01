git clone https://github.com/AInoriex/crawler_youtube_downloader.git
crawler_youtube_downloader/deploy.ps1
cd crawler_youtube_downloader

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
sleep 2
.venv\Scripts\yt-dlp --username oauth2 https://www.youtube.com/watch?v=3ZXxN4zzTz8