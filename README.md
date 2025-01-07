# Magic Crawler下载器

------



## 概述

​	本项目为数据采集下载的工作流。用于从数据库获取待处理任务，根据任务源类型不同并采用工具下载视频到本地，并上传云端对象存储服务，更新数据库信息。

> 目前支持的平台
>
> 1. [✔] Youtube 油管
> 2. 



## 环境依赖

2. ffmpeg
2. Python 推荐3.10+
2. Python 第三方依赖包详见`requirements.txt`



## 使用方法以及配置

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
   LARK_INFO_WEBHOOK=***https://open.feishu.cn/open-apis/bot/v2/hook/xxx***
   LARK_ERROR_WEBHOOK=***https://open.feishu.cn/open-apis/bot/v2/hook/xxx***
   
   # 对象存储类型(OBS华为云或者COS腾讯云二选一)
   # OBS
   OBS_ON=True
   OBS_ACESSKEY=***OBS_ACESS_KEY***
   OBS_SECRETKEY=***OBS_SECRET_KEY***
   OBS_HOST=***OBS_HOST***
   OBS_BUCKET=***OBS_BUCKET***
   OBS_URLBASE=***OBS_URLBASE***
   OBS_SAVEPATH=***OBS_SAVEPATH***
   
   # COS
   OBS_ON=False
   COS_ACESSKEY=***COS_ACESS_KEY***
   COS_SECRETKEY=***COS_SECRET_KEY***
   COS_BUCKET=***COS_BUCKET***
   COS_URLBASE=***COS_URLBASE***
   COS_SAVEPATH=***COS_SAVEPATH***
   
   # YOUTUBE CONFIG
   YTB_MAX_RETRY=
   ```

4. 目前支持的爬取模式（详见`ytb_download_pipeline.py youtube_download_handler方法`）

   1. yt_dlp，对应.env配置项如下
   
      ```
      YTB_DOWNLOAD_MODE=yt_dlp
      ```
   
   2. tubedown
   
      ```
      YTB_DOWNLOAD_MODE=tubedown
      ```
   
   3. rapidapi（推荐）
   
      ```
      YTB_DOWNLOAD_MODE=rapidapi
      ```
   
   4. yt_api（推荐）
   
      ```
      YTB_DOWNLOAD_MODE=yt_api
      ```
   
      
   
4. 确定好.env配置文件准确无误可执行程序

   ```bash
   python ytb_download.py
   ```






## 可能遇到的问题

1. 提示报错：`Sign in to confirm you’re not a bot. This helps protect our community.`

   - 插件已失效 

   - ~~使用 `OAuth2` 校验插件，详见 https://github.com/coletdjnz/yt-dlp-youtube-oauth2~~

     - ~~安装~~

       ```bash
       python -m pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip
       ```

     - ~~使用参数`--username oauth2 --password ''` 执行 `yt-dlp`~~

       ```bash
       yt-dlp --username oauth2 --password '' --cache-dir ./cache/yt-dlp https://www.youtube.com/watch?v=TImtNKeNk78
       ```

     - ~~首次使用需要在 https://www.google.com/device 添加设备码~~

     - ~~通过后账号token缓存在 `./cache/yt-dlp` 目录中~~

2. 



## 特别鸣谢

- [yt-dlp/yt-dlp: A feature-rich command-line audio/video downloader (github.com)](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp-youtube-oauth2](https://github.com/coletdjnz/yt-dlp-youtube-oauth2)

​	