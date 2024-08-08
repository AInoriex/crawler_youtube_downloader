#!/bin/bash

echo "初始化系统环境..."
# 添加 deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
# 更新包列表
sudo apt update

# 安装 Python 3.11 和虚拟环境包
sudo apt install python3.11 -y
sudo apt install python3.11-venv -y
# 检查 Python 版本
/usr/bin/python3.11 -V

# 安装 FFmpeg
sudo apt install ffmpeg -y
# 检查 FFmpeg 版本
ffmpeg -version

# 其他工具
sudo apt install tree
echo "初始化系统环境完毕"

# ------------------------------- #

echo "准备拉取仓库代码..."
mkdir /xyh
cd /xyh
git clone https://github.com/AInoriex/crawler_youtube_downloader
cd crawler_youtube_downloader
echo "拉取仓库代码完毕"

# ------------------------------- #

echo "准备初始化Python环境..."
/usr/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip -V
pip install -r requirements.txt 
pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip
echo "初始化Python环境完毕"

# ------------------------------- #

echo "准备添加OAuth2设备信息..."
mkdir -p ./cache/yt-dlp_1
mkdir -p ./cache/yt-dlp_2
tree -af ./cache
.venv/bin/yt-dlp --username oauth2 --password '' --output ./download/test_oauth2.mp4 --cache-dir ./cache/yt-dlp_1 https://www.youtube.com/watch?v=2mWbEZjqCYk
.venv/bin/yt-dlp --username oauth2 --password '' --output ./download/test_oauth2.mp4 --cache-dir ./cache/yt-dlp_2 https://www.youtube.com/watch?v=2mWbEZjqCYk
tree -ah ./cache

echo "scripts execute finished."