# 引入模块
import os
from obs import ObsClient
from obs import PutObjectHeader
from dotenv import load_dotenv
from urllib.parse import urljoin
import traceback
load_dotenv()

# 初始化读取配置文件
# 推荐通过环境变量获取AKSK，这里也可以使用其他外部引入方式传入，如果使用硬编码可能会存在泄露风险。
# 您可以登录访问管理控制台获取访问密钥AK/SK，获取方式请参见https://support.huaweicloud.com/intl/zh-cn/usermanual-ca/ca_01_0003.html。
ak = os.getenv("OBS_ACESSKEY")
sk = os.getenv("OBS_SECRETKEY")

# 【可选】如果使用临时AKSK和SecurityToken访问OBS，则同样推荐通过环境变量获取
# security_token = os.getenv("SecurityToken")

# server填写Bucket对应的Endpoint, 这里以中国-香港为例，其他地区请按实际情况填写。
# server = "https://obs.ap-southeast-1.myhuaweicloud.com" 
server = os.getenv("OBS_HOST")
bucket = os.getenv("OBS_BUCKET")

# 获取上传对象的进度
def callback(transferredAmount, totalAmount, totalSeconds):
    # 获取上传平均速率(KB/S)
    # print(transferredAmount * 1.0 / totalSeconds / 1024)
    trans_speed = transferredAmount * 1.0 / totalSeconds / 1024
    # 获取上传进度百分比
    # print(transferredAmount * 100.0 / totalAmount)
    trans_percent = transferredAmount * 100.0 / totalAmount
    print(f"Obs > upload_file callback {trans_speed:.2f}KB/s | {trans_percent:.2f}%")

# 上传
def upload_file(from_path:str, to_path:str)->str:
    """
    上传文件到OBS（单个文件大小须小于5G）
    :param from_path: 文件/文件夹的完整路径
    :param to_path: 对象名，即上传后的文件名
    :return: 上传后的文件url
    """
    if to_path.startswith("/"):
        to_path = to_path.replace("/", "", 1)
    try:
        # 创建obsClient实例
        # 如果使用临时AKSK和SecurityToken访问OBS，需要在创建实例时通过security_token参数指定securityToken值
        obsClient = ObsClient(access_key_id=ak, secret_access_key=sk, server=server)
        # 上传对象的附加头域
        headers = PutObjectHeader()
        # 【可选】待上传对象的MIME类型
        # headers.contentType = 'text/plain'
        bucketName = bucket
        # 对象名，即上传后的文件名
        # objectKey = "/data/test.txt"
        objectKey = to_path
        # 待上传文件/文件夹的完整路径，如aa/bb.txt，或aa/
        # file_path = 'download/test.txt'
        file_path = from_path
        # 【可选】上传文件的自定义元数据
        # metadata = {'meta1': 'value1', 'meta2': 'value2'}
        # 文件上传
        resp = obsClient.putFile(bucketName, objectKey, file_path, metadata=None, headers=headers, progressCallback=callback)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            print('Obs > 上传OBS成功')
            # print('requestId:', resp.requestId)
            # print('etag:', resp.body.etag)
            # print('versionId:', resp.body.versionId)
            # print('storageClass:', resp.body.storageClass)
        else:
            # print('Put File Failed')
            # print('requestId:', resp.requestId)
            # print('errorCode:', resp.errorCode)
            # print('errorMessage:', resp.errorMessage)
            raise Exception(f"上传OBS失败, resp:{resp.status} {resp.errorCode} {resp.errorMessage} {resp.requestId}")
    except Exception as e:
        print('Obs > 上传失败' + traceback.format_exc())
        raise e
    else:
        return urljoin(os.getenv("OBS_URLBASE"), to_path)

    finally:
        # 关闭obsClient
        obsClient.close()

def upload_file_v2(from_path:str, to_path:str)->str:
    """
    上传文件到OBS（适用于大于5G大文件上传）
    :param from_path: 文件/文件夹的完整路径
    :param to_path: 对象名，即上传后的文件名
    :return: 上传后的文件url
    """
    if to_path.startswith("/"):
            to_path = to_path.replace("/", "", 1)
    try:
        obsClient = ObsClient(access_key_id=ak, secret_access_key=sk, server=server)
        bucketName = bucket
        objectKey = to_path
        uploadFile = from_path
        # 分段上传的并发数
        taskNum = 5
        # 分段的大小，单位字节，此处为10MB
        partSize = 10 * 1024 * 1024
        # True表示开启断点续传
        enableCheckpoint = True
        # 断点续传上传
        resp = obsClient.uploadFile(bucketName, objectKey, uploadFile, partSize, taskNum, enableCheckpoint, encoding_type='url')

        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            print('Obs > 上传OBS成功')
            print(f'from_path: {from_path}, to_path: {to_path}')
        else:
            print('Obs > [!] 上传OBS失败')
            print('requestId:', resp.requestId)
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
            raise Exception(f"上传OBS失败, resp:{resp.status} {resp.errorCode} {resp.errorMessage} {resp.requestId}")
    except Exception as e:
        print('Obs > 上传失败' + traceback.format_exc())
        raise e
    else:
        return urljoin(os.getenv("OBS_URLBASE"), to_path)
    finally:
        # 关闭obsClient
        obsClient.close()