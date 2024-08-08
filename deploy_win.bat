echo "ready to check env"
timeout /t 3 /nobreak
py -3 -V
ffmpeg -version

echo "ready to create venv"
timeout /t 3 /nobreak
py -3 -m venv .venv
.venv\Scripts\pip -V

echo "ready to install venv requirements"
timeout /t 3 /nobreak
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip

echo "ready to add google device code"
tree /F ./cache
mkdir .\cache\yt-dlp_1
mkdir .\cache\yt-dlp_2
tree /F ./cache
timeout /t 3 /nobreak

.venv\Scripts\yt-dlp --username oauth2 --password '' --cache-dir ./cache/yt-dlp_1  --paths ./download/ https://www.youtube.com/watch?v=2mWbEZjqCYk
.venv\Scripts\yt-dlp --username oauth2 --password '' --cache-dir ./cache/yt-dlp_2  --paths ./download/ https://www.youtube.com/watch?v=2mWbEZjqCYk
tree /F ./cache

timeout /t 3 /nobreak
echo "scripts execute finished."