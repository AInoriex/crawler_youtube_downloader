import os

def list_files(directory):
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return files

directory = 'download'  # 你要扫描的目录
all_files = list_files(directory)

for file in all_files:
    print(file)
