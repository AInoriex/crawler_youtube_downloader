# pip install mysql-connector-python

import time
import random
from os import getenv
from mysql.connector.pooling import MySQLConnection
from mysql.connector import Error
from typing import List
from database.db_manager import DatabaseManager

TABLE_NAME = str("crawler_download_info")

class Video:
    """
    视频数据

    Attributes:
        vid: 视频ID
        source_type: 1: Bilibili, 2: 喜马拉雅, 3: YouTube
        link: 完整视频链接
        path: 本地路径
        position: 存储位置
        cloud_type: 1: cos, 2: obs
        cloud_path: 云存储的路径
        result_path: 处理结果路径
        duration: 原始长度
        duration: 有效长度
        language: 视频主要语言
        status: 0: 已爬取, 1: 本地已下载, 2: 已上传云端未处理, 3: 已处理未上传, 4: 已处理已上传
        lock: 处理锁, 0: 未锁定, 1: 锁定, 2: 错误
        info: meta数据, json格式
    """

    def __init__(
        self,
        vid: str,
        source_type: int,
        cloud_path: str,
        id: int = 0,
        position: int = 1,
        cloud_type: int = None,
        source_link: str = None,
        duration: int = None,
        language: str = None,
        status=0,
        lock=0,
        info="{}",
    ):
        self.id = id
        self.vid = vid
        self.position = position
        self.source_type = source_type
        self.source_link = source_link
        self.duration = duration
        self.cloud_type = cloud_type
        self.cloud_path = cloud_path
        self.language = language
        self.status = status
        self.lock = lock
        self.info = info

    def __str__(self) -> str:
        return (
            f"Video(vid={self.vid}, position={self.position}, "
            f"source_type={self.source_type}, source_link={self.source_link}, duration={self.duration}, "
            f"cloud_type={self.cloud_type}, cloud_path={self.cloud_path}, "
            f"language={self.language}, status={self.status}, `lock`={self.lock}, info={self.info})"
        )

# Using the DatabaseManager
if getenv("DATABASE_GET_API") == '':
    db_manager = DatabaseManager()

# Create
def create_video(video: Video):
    sql = f"""
    INSERT INTO `{TABLE_NAME}` (vid, position, source_type, source_link, duration, cloud_type, cloud_path, language, status, `lock`, info)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    video_data = (
        video.vid,
        video.position,
        video.source_type,
        video.source_link,
        video.duration,
        video.cloud_type,
        video.cloud_path,
        video.language,
        video.status,
        video.lock,
        video.info,
    )
    db_manager.insert(sql, video_data)


def get_video_by_vid(vid):
    try:
        conn: MySQLConnection = db_manager.get_connection()
        # cursor = conn.cursor()
        cursor = db_manager.execute_query(
            f"SELECT id, vid, position, source_type, source_link, duration, cloud_type, cloud_path, language, status, `lock`, info FROM `{TABLE_NAME}` WHERE vid = %s",
            (vid,),
        )
        records = cursor.fetchone()
        if records is None:
            # print("Video not found")
            return None
        # id, *record = records
        _, *record = records
        video = Video(*record)
        print("Video Retrieved:", video)
    except Exception as e:
        print(f"get_video_by_vid error: {e.__str__}")
        return None
    else:
        return video
    finally:
        if conn:
            cursor.close()
            conn.close()


def update_video_by_id(id, new_data):
    updates = ", ".join([f"`{key}` = %s" for key in new_data])
    values = list(new_data.values())

    values.append(id)

    sql = f"UPDATE `{TABLE_NAME}` SET {updates} WHERE id = %s"

    db_manager.update(sql, values)
    # print("Video updated successfully")

def update_video_by_vid(vid, new_data):
    updates = ", ".join([f"`{key}` = %s" for key in new_data])
    values = list(new_data.values())

    values.append(vid)

    sql = f"UPDATE `{TABLE_NAME}` SET {updates} WHERE vid = %s"

    db_manager.update(sql, values)
    # print("Video updated successfully")


def delete_video(vid):
    sql = f"DELETE FROM `{TABLE_NAME}` WHERE vid = %s"
    db_manager.delete(sql, (vid,))


update_info = {}


def update_total_count(where_query):
    global update_info

    last_update_time, total_count_cache = update_info.get(where_query, (0, 0))

    current_time = time.time()
    # 如果超过一小时，则更新count
    if current_time - last_update_time > 3600 or total_count_cache == 0:
        # conn: MySQLConnection = db_manager.get_connection()
        # cursor = conn.cursor()
        cursor = db_manager.execute_query(
            f"""
            SELECT COUNT(*)
            FROM `{TABLE_NAME}`
            {where_query}
        """
        )
        total_count_cache = cursor.fetchone()[0]
        last_update_time = current_time
        if total_count_cache == 0:
            print("No available audio found, sleeping for 60 seconds...")
            time.sleep(60)
        if total_count_cache > 1000:
            print("Total count:", total_count_cache, "Resetting to 1000")
            total_count_cache = 1000

        update_info[where_query] = (last_update_time, total_count_cache)


def get_next_audio(where_query, lock=True):
    global update_info
    update_total_count(where_query)  # 确保count是最新的

    none_return = (None, None, None, None)

    total_count_cache = update_info[where_query][1]

    if total_count_cache == 0:
        return none_return

    # 随机生成一个偏移量
    random_offset = random.randint(0, total_count_cache - 1)

    try:
        conn: MySQLConnection = db_manager.get_connection()
        # 开启事务
        if lock:
            conn.start_transaction()

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT id, vid, cloud_path, status, source_link
            FROM `{TABLE_NAME}`
            {where_query}
            LIMIT {random_offset}, 1
        """
        )

        # 随机选择一条符合条件的记录
        record = cursor.fetchone()

        if record is None:
            if lock:
                conn.rollback()
            return none_return

        id, vid, cloud_path, status, source_link = record

        if not lock:
            # return vid, cloud_path, source_link, status
            return id, cloud_path, source_link, status

        # 尝试更新锁状态
        cursor.execute(
            f"""
            UPDATE `{TABLE_NAME}`
            SET `lock` = 1
            WHERE id = %s AND `lock` = 0
        """,
            (id,),
        )
        update_count = cursor.rowcount

        # 如果更新成功，则提交事务
        if update_count == 1:
            conn.commit()
            print("Video Retrieved:", id, cloud_path, status)
            # return vid, cloud_path, source_link, status
            return id, cloud_path, source_link, status
        else:
            # 否则回滚事务
            conn.rollback()
            return none_return

    except Exception as e:
        # 发生错误时回滚事务
        if lock:
            conn.rollback()
        # raise e
        return none_return
    finally:
        if conn:
            conn.close()


# # 处理成功更新
# def uploaded_audio(vid, cloud_path, path=None):
#     sql = f"UPDATE `{TABLE_NAME}` SET path = %s, cloud_path = %s, status = 2, `lock` = 0 WHERE vid = %s"
#     db_manager.update(sql, (path, cloud_path, vid))

# # 处理失败更新
# def failed_audio(vid):
#     sql = f"UPDATE `{TABLE_NAME}` SET `lock` = 2 WHERE vid = %s"
#     db_manager.update(sql, (vid,))

# # 数据解锁
# def revert_audio(vid):
#     sql = f"UPDATE `{TABLE_NAME}` SET `lock` = 0 WHERE vid = %s"
#     db_manager.update(sql, (vid,))

# 处理成功更新
def uploaded_download(id, cloud_type, cloud_path, path=None):
    sql = f"UPDATE `{TABLE_NAME}` SET cloud_type = %s, cloud_path = %s, status = 2, `lock` = 0 WHERE id = %s"
    db_manager.update(sql, (cloud_type, cloud_path, id))

# 处理失败更新
def failed_download(id):
    sql = f"UPDATE `{TABLE_NAME}` SET `lock` = 2 WHERE id = %s"
    db_manager.update(sql, (id,))

# 数据解锁
def revert_download(id):
    sql = f"UPDATE `{TABLE_NAME}` SET `lock` = 0 WHERE id = %s"
    db_manager.update(sql, (id,))


# Example Usage
video_data = Video(
    vid="VID12345",
    position=1,
    source_type=1,
    source_link="https://www.youtube.com/watch?v=12345",
    duration=100,
    cloud_type=2,
    cloud_path="/cloud/path/to/video",
    language="en",
    status=0,
    lock=0,
    info='{"key": "value"}',
)


if __name__ == "__main__":
    create_video(video_data)
    # get_video_by_vid("VID12345")
    # update_video("VID12345", {"path": "/test", "position": 2, "status": 1})
    # delete_video("VID12345")
    get_video_by_vid("VID12345")
    pass
