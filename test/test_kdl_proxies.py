import requests
import time
import os
from test_download import download_file

test_folder = os.path.join(os.getcwd(), "kuaidaili")
kdl_ip_list = [
    "http://qgjhxrjd635c:isbq4qrv0u7g@104.234.164.50:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@104.234.164.158:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@104.234.221.54:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@104.234.221.82:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@104.234.121.115:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@206.237.68.185:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@206.237.68.241:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@206.237.69.2:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@206.237.70.59:2333/",
    "http://qgjhxrjd635c:isbq4qrv0u7g@206.237.71.152:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@38.181.114.46:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@38.181.114.213:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@38.181.115.111:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@38.181.115.183:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@38.181.120.52:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@38.181.120.62:2333/",
    "http://qgjhx3t36jcx:tfmr91cf5roo@38.181.120.96:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@38.181.120.153:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@38.181.120.160:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@38.181.120.210:2333/",
    "http://qgjhx3t36jcx:tfmr91cf5roo@149.40.69.80:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@149.40.69.167:2333/",
    "http://qgjhx3t36jcx:tfmr91cf5roo@149.40.69.232:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@149.40.83.13:2333/",
    "http://qgjhx3t36jcx:tfmr91cf5roo@149.40.83.22:2333/",
    "http://egjhx35zaa64:bmeb5b268q5j@149.40.83.248:2333/",
    "http://qgjhx3t36jcx:tfmr91cf5roo@149.40.83.249:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@149.40.84.151:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@149.40.84.177:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@149.40.87.48:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@149.40.87.140:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.85.104.183:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.195.8.36:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.195.9.118:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.195.10.179:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.195.11.191:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.208.0.33:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.212.12.102:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.212.13.52:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.212.14.2:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.212.15.89:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.214.16.157:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@154.214.18.76:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@156.238.122.42:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@156.238.122.147:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@156.238.123.167:2333/",
    "http://cgjhx9jxn3xy:piez4h5uesrv@156.238.123.208:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@156.248.104.240:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@156.248.109.126:2333/",
    "http://ngjhx3yf9zss:zgxhspq6pob1@156.248.110.134:2333/",
]
# kdl_ip_list = ["10.200.0.33:7890"]
kdl_ip_list = ["127.0.0.1:7890"]

video_url = "https://rr2---sn-uxax4vopj5qx-q0n6.googlevideo.com/videoplayback?expire=1733844465&ei=kQlYZ9iyAumy6dsP9u_k0AM&ip=176.1.249.199&id=o-ADesNKAwOvvj5ONEQZJwYK860S2bVYm7KeFyOLG_9yl5&itag=18&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1733822865%2C&mh=pU&mm=31%2C29&mn=sn-uxax4vopj5qx-q0n6%2Csn-4g5ednde&ms=au%2Crdu&mv=m&mvi=2&pcm2cms=yes&pl=17&rms=au%2Cau&initcwndbps=938750&bui=AQn3pFSJzCKQtW1mntYJNjJ7qHKwZbpWrJe-88ITR_ic0mw-0-A4OWyl24tK84EJiPkqJDz7zosR_nW-&spc=qtApAbp0YOKd-7ADLdDhbCi0pPN7FnzJdrQ2yBg3zM0i6j1yNj8D&vprv=1&svpuc=1&mime=video%2Fmp4&ns=BG4P-6b0pv_wF-FAFVrhe70Q&rqh=1&gir=yes&clen=52924240&ratebypass=yes&dur=983.806&lmt=1731011042388427&mt=1733822686&fvip=3&fexp=51326932%2C51335594%2C51347747%2C51355912&c=WEB&sefc=1&txp=5538434&n=2EMB609J1sSXSA&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=AJfQdSswRAIgMzouS2VeOL4ElqNJG41lzQSqFMShKxK9XpqkVvFLZEQCIFdJ_T50Ru8inUL9RVieTfTx4pCznp4LNQ6zPRQ3mIWj&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpcm2cms%2Cpl%2Crms%2Cinitcwndbps&lsig=AGluJ3MwRQIgQ9KfuwhfY7rlJFr1ZSq9qeoCfP8M92Tg6LMpBdXBtXYCIQDHL7-3lHmoecmp07JXrWZu3qSQhYibZS5VkCTaE-volg%3D%3D"

if __name__ == "__main__":
    index = 0
    result_path = os.path.join(test_folder, "result.txt")
    task_id = int(time.time())
    date_time_string = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    with open(result_path, "a", encoding="utf-8") as f:
        f.write(f"----------- 任务批次：{task_id} -----------\n")
        f.write(f"> 测试时间：{date_time_string}\n")
        f.write(f"> 测试URL: {video_url}\n")
        f.write(f"> 测试代理数量: {len(kdl_ip_list)}\n")
        for ip in kdl_ip_list:
            print(f"当前测试IP: {ip}")
            try:
                index += 1
                tmpfile = os.path.join(test_folder, "tmp", f"{task_id}_{index}.mp4")

                proxies={
                    'http': ip,
                    'https': ip,
                }
                account = download_file(video_url, tmpfile, proxies=proxies)

                print(f"[SUCC] {index} | {ip}")
                f.write(f"[SUCC] {index} | {ip}")
                f.write("\n")
            except Exception as e:
                os.open(os.path.join(test_folder, "tmp", f"{task_id}_{index}.mp4.fail"), os.O_CREAT)
                print(f"[FAIL] {index} | {ip} > {e}")
                f.write(f"[FAIL] {index} | {ip} > {e}")
                f.write("\n")
            finally:
                f.flush()
                time.sleep(2)
        f.write("\n")

    print(f"----------- 程序结束 -----------")