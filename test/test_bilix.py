from bilix.utils import legal_title, t2s
from bilix.sites.bilibili import api, DownloaderBilibili
from bilix.exception import (
    APIUnsupportedError,
    APIResourceError,
)
from bilix.download.utils import path_check
from bilix import ffmpeg

import os
import asyncio
import json
from typing import Union, Tuple, List
from pathlib import Path

# from handler.info import dump_info


class Downloader(DownloaderBilibili):
    async def get_video(
        self,
        url: str,
        path=Path("."),
        quality: Union[str, int] = 0,
        codec: str = "",
        video_info: api.VideoInfo = None,
    ):
        """
        下载单个视频
        :cli: short: v
        :param url: 视频的url
        :param path: 保存路径
        :param quality: 画面质量，0为可以观看的最高画质，越大质量越低，超过范围时自动选择最低画质，或者直接使用字符串指定'1080p'等名称
        :param codec: 视频编码（可通过codec获取）
        :param video_info: 额外数据，提供时不用再次请求页面
        :return:
        """
        async with self.v_sema:
            if not video_info:
                try:
                    video_info = await api.get_video_info(self.client, url)
                except (APIResourceError, APIUnsupportedError) as e:
                    return self.logger.warning(e)
            p_name = legal_title(video_info.pages[video_info.p].p_name)
            task_name = legal_title(video_info.title, p_name)
            # if title is too long, use p_name as base_name
            # base_name = (
            #     p_name
            #     if len(video_info.title) > self.title_overflow
            #     and self.hierarchy
            #     and p_name
            #     else task_name
            # )
            base_name = video_info.bvid
            media_name = base_name
            media_cors = []
            task_id = await self.progress.add_task(total=None, description=task_name)
            if video_info.dash:
                try:  # choose video quality
                    video, audio = video_info.dash.choose_quality(quality, codec)
                except KeyError:
                    self.logger.warning(
                        f"{task_name} 清晰度<{quality}> 编码<{codec}>不可用，请检查输入是否正确或是否需要大会员"
                    )
                else:
                    tmp: List[Tuple[api.Media, Path]] = []
                    # 1. only audio
                    if audio:
                        tmp.append((audio, path / f"{media_name}{audio.suffix}"))
                    else:
                        self.logger.warning(f"No audio for {task_name}")
                    # convert to coroutines
                    media_cors.extend(
                        self.get_file(t[0].urls, path=t[1], task_id=task_id)
                        for t in tmp
                    )

            elif video_info.other:
                self.logger.warning(
                    f"{task_name} 未解析到dash资源，转入durl mp4/flv下载（不需要会员的电影/番剧预览，不支持dash的视频）"
                )
                media_name = base_name
                if len(video_info.other) == 1:
                    m = video_info.other[0]
                    media_cors.append(
                        self.get_file(
                            m.urls,
                            path=path / f"{media_name}.{m.suffix}",
                            task_id=task_id,
                        )
                    )
                else:
                    exist, media_path = path_check(path / f"{media_name}.mp4")
                    if exist:
                        self.logger.info(f"[green]已存在[/green] {media_path.name}")
                    else:
                        p_sema = asyncio.Semaphore(self.part_concurrency)

                        async def _get_file(media: api.Media, p: Path) -> Path:
                            async with p_sema:
                                return await self.get_file(
                                    media.urls, path=p, task_id=task_id
                                )

                        for i, m in enumerate(video_info.other):
                            f = f"{media_name}-{i}.{m.suffix}"
                            media_cors.append(_get_file(m, path / f))
                        await self.progress.update(task_id=task_id, upper=ffmpeg.concat)
            else:
                self.logger.warning(f"{task_name} 需要大会员或该地区不支持")

            path_lst = await asyncio.gather(*media_cors)

        if upper := self.progress.tasks[task_id].fields.get("upper", None):
            await upper(path_lst, media_path)
            self.logger.info(f"[cyan]已完成[/cyan] {media_path.name}")
        await self.progress.update(task_id, visible=False)
        return video_info, path_lst

# 预创建下载目录
def make_path(save_path):
    save_audio_path = os.path.join(save_path, "audio")
    save_info_path = os.path.join(save_path, "info")
    os.makedirs(save_audio_path, exist_ok=True)
    os.makedirs(save_info_path, exist_ok=True)
    return save_audio_path, save_info_path


def generate_video_info(video_info: api.VideoInfo):
    info_dict = {
        "id": video_info.aid,
        "title": video_info.title,
        "full_url": f"https://www.bilibili.com/video/{video_info.bvid}",
        "author": None,
        "duration": None,
        "categories": None,
        "tags": video_info.tags,
        "view_count": video_info.status.view,
        "comment_count": video_info.status.reply,
        "follower_count": None,
        "upload_date": None,
    }
    return info_dict


def download(url, save_path):
    return download_by_url(url, save_path)


def download_by_url(video_url, save_path):
    save_audio_path, save_info_path = make_path(save_path)
    target_path = os.path.join(save_audio_path, os.path.basename(video_url).split('?')[0]+'.aac')
    if os.path.exists(target_path):
        print("{} already downloaded".format(target_path))
        return None

    async def download():
        async with Downloader() as d:
            print("Downloading video...")
            return await d.get_video(video_url, path=save_audio_path)

    # run the async function in the event loop
    try:
        video_info, path_lst = asyncio.run(download())
    except Exception as e:
        print(e)
        print(e.__str__)
        return None
    

    vid = video_info.bvid

    info_dict = generate_video_info(video_info)

    save_to_json_file = f"{save_info_path}/{vid}.json"

    print(info_dict)

    result_path = [str(p) for p in path_lst]

    dump_info(info_dict, save_to_json_file)

    # print("Downloaded video to", result_path)
    # print("Downloaded video info to", save_to_json_file)
    return result_path

def dump_info(info_dict, out_file):
    ''' 保存json文件到本地
    @info_dict: 待打包服务
    @out_file: 保存路径
    '''
    with open(out_file, "w", encoding="utf8") as out:
        json.dump(info_dict, out, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    print(
        download_by_url(
            video_url="https://www.bilibili.com/bangumi/play/ep718277?spm_id_from=trigger_reload",
            save_path="./download",
        )
    )
