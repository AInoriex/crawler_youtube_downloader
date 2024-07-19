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

3. 运行程序

4. （施工中...）



## 特别鸣谢

​	[yt-dlp/yt-dlp: A feature-rich command-line audio/video downloader (github.com)](https://github.com/yt-dlp/yt-dlp)

​	