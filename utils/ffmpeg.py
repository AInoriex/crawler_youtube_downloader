import subprocess
from os import path
from uuid import uuid4
from utils.logger import logger

def merge_video_with_audio(video_path:str, audio_path:str, dst_path:str)->str:
    """ 合并视频和音频 """
    if video_path == "" or audio_path == "":
        raise ValueError(f"merge_video_with_audio params invalid, video_path:{video_path}, audio_path:{audio_path}")
    if dst_path == "":
        dst_path = path.join(path.dirname(video_path), f"{uuid4()}.mp4")
    # 构建ffmpeg命令
    command = [
        'ffmpeg',
        '-i', video_path,  # 输入的视频文件
        '-i', audio_path,  # 输入的音频文件
        '-c:v', 'copy',    # 复制视频流
        '-c:a', 'aac',     # 使用AAC编码音频流
        '-strict', 'experimental',  # 某些版本的ffmpeg需要这个参数来启用aac编码
        '-y', dst_path  # 输出文件路径
    ]

    # 调用ffmpeg命令
    try:
        subprocess.run(command, check=True)
        logger.info(f"merge_video_with_audio ffmpeg merge success, result dst_path:{dst_path}")
        return dst_path
    except subprocess.CalledProcessError as e:
        logger.error(f"merge_video_with_audio error, {video_path} + {audio_path} => {dst_path}, error:{e}")
        raise e