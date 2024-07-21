# 油管下载器

## Description

​	本项目用于批量从数据库获取待下载链接，并采用 `yt-dlp` 工具下载油管视频到本地，并上传云端(OBS or COS)



## Usage

1. 安装第三方依赖包

   ```
   pip install -r requirements.txt
   ```

2. 创建 `.env` 配置文件在根目录，样例如下

   ```
   # .env
   
   # COMMON
   DEBUG=True
   LOG_PATH=logs
   DOWNLOAD_PATH=download
   TMP_FOLDER_PATH=temp
   HTTP_PROXY=
   
   # DATABASE
   DATABASE_HOST=
   DATABASE_PORT=3306
   DATABASE_USER=
   DATABASE_PASS=
   DATABASE_DB=crawler
   ```

3. 安装反BOT校验插件，详见 https://github.com/coletdjnz/yt-dlp-youtube-oauth2

   ```python
   python3 -m pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip
   ```

   - 使用参数`--username oauth2 --password ''` 执行 `yt-dlp`
   - 首次使用在 https://www.google.com/device 添加设备码

3. 运行程序

4. （施工中...）



## 特别鸣谢

​	[yt-dlp/yt-dlp: A feature-rich command-line audio/video downloader (github.com)](https://github.com/yt-dlp/yt-dlp)

​	