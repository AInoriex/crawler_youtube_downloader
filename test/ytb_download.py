def ytb_download():
    # 调用接口获取待处理数据

    # 油管链接格式化
    # url = "https://www.youtube.com/watch?v=tXuPmu2Sa60&list=PLRMEKqidcRnBaMTFQzWkXpNk8_xF3QvMZ"
    # url = "https://www.youtube.com/watch?v=tXuPmu2Sa60"
    url = "https://www.youtube.com/watch?v=6s416NmSFmw&list=PLRMEKqidcRnAGC6j1oYPFV9E26gyWdgU4&index=4"
    url = format_into_watch_url(url)

    # 下载处理
    ytb_watch_url = download(url)