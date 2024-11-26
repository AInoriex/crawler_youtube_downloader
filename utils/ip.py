import socket
import json
import requests
 
def get_local_ip()->str:
    ''' 获取本机IP地址 '''
    try:
        hostname = socket.gethostname()  # 获取本机主机名
        local_ip = socket.gethostbyname(hostname)  # 通过主机名获取本机IP地址
        # print("本机IP地址：", local_ip)
        return local_ip
    except requests.exceptions.RequestException:
        pass
    return ""
 
def get_public_ip()->str:
    try:
        response = requests.get('https://httpbin.org/ip', timeout=5)
        # print(response.status_code, response.content)
        if response.status_code == 200:
            resp = response.json()
            return resp['origin']
    except:
        return ""
 
if __name__ == '__main__':
    external_ip = get_public_ip()
    if external_ip:
        print(f"Ip > Your outbound IP address is: {external_ip}")
    else:
        print("Ip > Unable to retrieve your outbound IP address.")