# Magic Crawler下载器

------



## Description

​	本项目用于从数据库获取待下载链接，并采用 `yt-dlp` 工具下载视频到本地，并上传云端(OBS or COS)

​	目前支持的平台：Youtube 油管



## 环境要求

1. Python 3.x
2. FFmpeg



## Usage

1. 安装第三方依赖包

   ```
   pip install -r requirements.txt
   ```

2. 在根目录创建`.env`配置文件，样例如下

   ```yaml
   # .env example
   
   # COMMON
   SERVER_NAME=***INPUT_YOUR_SERVE_NAME***
   DEBUG=True
   LOG_PATH=logs
   DOWNLOAD_PATH=download
   TMP_FOLDER_PATH=temp
   HTTP_PROXY=
   PROCESS_NUM=5
   LIMIT_FAIL_COUNT=5
   LIMIT_LAST_COUNT=10
   
   # DATABASE
   DATABASE_GET_API=***https://xxx.com/api/ytb_get_download_list***
   DATABASE_UPDATE_API=***https://xxx.com/api/ytb_update_status***
   
   # LARK
   LARK_NOTICE_WEBHOOK=***https://open.feishu.cn/open-apis/bot/v2/hook/xxx***
   LARK_ERROR_WEBHOOK=***https://open.feishu.cn/open-apis/bot/v2/hook/xxx***
   
   # OBS
   OBS_ON=False
   OBS_ACESSKEY=***OBS_ACESS_KEY***
   OBS_SECRETKEY=***OBS_SECRET_KEY***
   OBS_HOST=***OBS_HOST***
   OBS_BUCKET=***OBS_BUCKET***
   OBS_URLBASE=***OBS_URLBASE***
   OBS_SAVEPATH=***OBS_SAVEPATH***
   
   # COS
   COS_ACESSKEY=***COS_ACESS_KEY***
   COS_SECRETKEY=***COS_SECRET_KEY***
   COS_BUCKET=***COS_BUCKET***
   COS_URLBASE=***COS_URLBASE***
   COS_SAVEPATH=***COS_SAVEPATH***
   
   # YOUTUBE CONFIG
   YTB_DEBUG=True # ATTENTION
   YTB_MAX_RETRY=25
   YTB_OAUTH2_PATH=/tmp/cache/yt-dlp_account_1
   ```

3. *提示报错：`Sign in to confirm you’re not a bot. This helps protect our community.`

   - 使用 `OAuth2` 校验插件，详见 https://github.com/coletdjnz/yt-dlp-youtube-oauth2

      - 安装

        ```bash
        python -m pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip
        ```

      - 使用参数`--username oauth2 --password ''` 执行 `yt-dlp`

        ```bash
        yt-dlp --username oauth2 --password '' --cache-dir ./cache/yt-dlp https://www.youtube.com/watch?v=TImtNKeNk78
        ```

      - 首次使用需要在 https://www.google.com/device 添加设备码

      - 通过后账号token缓存在 `./cache/yt-dlp` 目录中

4. 启动程序

   ```bash
   python ytb_download.py
   ```

   

## 特别鸣谢

- [yt-dlp/yt-dlp: A feature-rich command-line audio/video downloader (github.com)](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp-youtube-oauth2](https://github.com/coletdjnz/yt-dlp-youtube-oauth2)

​	