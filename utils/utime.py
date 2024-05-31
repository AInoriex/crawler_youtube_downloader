# -*- coding: UTF8 -*-
import time
from utils.logger import init_logger
import random

logger = init_logger("utils/time")

def random_sleep(rand_range:int, rand_st:int):
    '''随机等待[rand_st, rand_st+rand_range]秒'''
    if rand_range < 1:
        rand_range = 5
    if rand_st < 1:
        rand_st = 5
    rand_range = random.randint(rand_st, rand_st + rand_range)
    logger.info(f"random_sleep {rand_range} seconds")
    time.sleep(rand_range)
    return

def get_now_time_string():
    ''' 返回现在时间戳字符串 | 格式：%年%月%日-%时:%分:%秒 '''
    return time.strftime("%Y%m%d-%H:%M:%S", time.localtime())

def get_now_time_string_short():
    ''' 返回现在时间戳字符串 | 格式：%年%月%日%时%分%秒 '''
    return time.strftime("%Y%m%d%H%M%S", time.localtime())