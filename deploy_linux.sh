#!/bin/bash

# echo "初始化环境..."

# # 添加 deadsnakes PPA
# sudo add-apt-repository ppa:deadsnakes/ppa -y
# # 更新包列表
# sudo apt update

# # 安装 Python 3.11 和虚拟环境包
# sudo apt install python3.11 -y
# sudo apt install python3.11-venv -y
# # 检查 Python 版本
# /usr/bin/python3.11 -V

# # 安装 FFmpeg
# sudo apt install ffmpeg -y
# # 检查 FFmpeg 版本
# ffmpeg -version

#echo "拉取仓库代码..."
# mkdir /xyh
# cd /xyh
# git clone https://github.com/AInoriex/crawler_youtube_downloader
# cd crawler_youtube_downloader

echo "初始化Python环境..."
/usr/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip -V
pip install -r requirements.txt 
pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip

echo "环境安装完毕，准备添加OAuth2设备信息..."
.venv\bin\yt-dlp --username oauth2 --output ./download https://www.youtube.com/watch?v=2mWbEZjqCYk
