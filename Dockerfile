# 使用Python 3.11作为基础镜像
FROM uhub.service.ucloud.cn/jackhe/python:3.11.9-slim

# 设置环境变量，避免Python生成.pyc文件
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建并设置工作目录
WORKDIR /app

# 将requirements.txt文件复制到容器中
COPY requirements.txt /app/

# 安装Python依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 将项目的源代码复制到容器中
COPY . /app/

# 指定默认命令来运行Python程序
CMD ["python", "/app/crawler_youtube_downloader/ytb_download_pipeline.py"]
