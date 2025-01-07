from os import path, makedirs, walk

def list_files(directory):
    files = []
    for dirpath, dirnames, filenames in walk(directory):
        for filename in filenames:
            files.append(path.join(dirpath, filename))
    return files

def create_youtuber_folder(save_path:str, title:str):
    try:
        print(f"create_youtuber_folder > 原始标题：{title}")
        title = title.replace('\\', '-') \
            .replace('/', '-').replace(':', '-') \
            .replace('*', '-').replace('?', '-') \
            .replace('"', '-').replace('<', '-') \
            .replace('>', '-').replace('|', '-')
        print(f"create_youtuber_folder > 格式化后标题：{title}")
        folder_path = path.join(save_path, title)
        print(f"create_youtuber_folder > 创建目录 {folder_path}")
        makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"create_youtuber_folder > 创建文件夹失败：{e}")

if __name__ == "__main__":
    directory = 'download'  # 你要扫描的目录
    all_files = list_files(directory)

    for file in all_files:
        print(file)

    title = "Youtuber | Khang Show"
    create_youtuber_folder(save_path=".", title=title)
