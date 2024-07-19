import json
import time


def dump_info(info_dict, out_file):
    with open(out_file, "w", encoding="utf8") as out:
        json.dump(info_dict, out, indent=4, ensure_ascii=False)


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
