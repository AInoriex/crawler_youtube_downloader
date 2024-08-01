from tqdm import tqdm

class UploadProgress:
    def __init__(self, totalAmount):
        self.totalAmount = totalAmount
        self.pbar = tqdm(total=totalAmount, unit='B', unit_scale=True, desc='Uploading', ncols=100)

    def __call__(self, transferredAmount, totalAmount, totalSeconds):
        # 更新进度条
        self.pbar.update(transferredAmount - self.pbar.n)
        
        # 获取上传平均速率(KB/S)
        avg_speed = transferredAmount * 1.0 / totalSeconds / 1024
        print(f"Average speed: {avg_speed:.2f} KB/s")

    def close(self):
        self.pbar.close()

# 示例使用方法
import time

# 假设文件总大小为 1000000 字节
total_size = 1000000
progress = UploadProgress(total_size)

for i in range(1, total_size + 1, 10000):
    time.sleep(0.1)  # 模拟上传时间
    progress(i, total_size, i * 0.01)  # 模拟 transferredAmount 和 totalSeconds

progress.close()