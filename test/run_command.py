import subprocess

def execute_command(command):
    try:
        # 执行命令，并等待其完成
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 如果命令执行成功，输出返回码和标准输出
        print(f"命令执行成功，返回码: {result.returncode}")
        if result.stdout:
            print(f"标准输出:\n{result.stdout.decode('utf-8')}")
        if result.stderr:
            print(f"标准错误:\n{result.stderr.decode('utf-8')}")
        
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，输出返回码和标准错误
        print(f"命令执行失败，返回码: {e.returncode}")
        if e.stdout:
            print(f"标准输出:\n{e.stdout.decode('utf-8')}")
        if e.stderr:
            print(f"标准错误:\n{e.stderr.decode('utf-8')}")

# 示例：执行一个简单的命令
# command_to_run = "echo 'hello'"
# command_to_run = "bilix.exe info https://www.bilibili.com/video/BV1aF411U7vL/?vd_source=789b2a4272ef157767bd312ef547be90"
command_to_run = "bilix.exe get_video https://www.bilibili.com/video/BV1aF411U7vL/?vd_source=789b2a4272ef157767bd312ef547be90 --image"
execute_command(command_to_run)
