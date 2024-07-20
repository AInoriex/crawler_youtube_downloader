# 引入模块
import os
from obs import ObsClient
from obs import PutObjectHeader
from dotenv import load_dotenv
import traceback
load_dotenv()

# 推荐通过环境变量获取AKSK，这里也可以使用其他外部引入方式传入，如果使用硬编码可能会存在泄露风险。
# 您可以登录访问管理控制台获取访问密钥AK/SK，获取方式请参见https://support.huaweicloud.com/intl/zh-cn/usermanual-ca/ca_01_0003.html。
ak = os.getenv("OBS_ACESSKEY")
sk = os.getenv("OBS_SECRETKEY")

# 【可选】如果使用临时AKSK和SecurityToken访问OBS，则同样推荐通过环境变量获取
# security_token = os.getenv("SecurityToken")

# server填写Bucket对应的Endpoint, 这里以中国-香港为例，其他地区请按实际情况填写。
# server = "https://obs.ap-southeast-1.myhuaweicloud.com" 
server = os.getenv("OBS_HOST")

# 创建obsClient实例
# 如果使用临时AKSK和SecurityToken访问OBS，需要在创建实例时通过security_token参数指定securityToken值
obsClient = ObsClient(access_key_id=ak, secret_access_key=sk, server=server)

# 使用访问OBS
try:
    # 上传对象的附加头域
    headers = PutObjectHeader()
    # 【可选】待上传对象的MIME类型
    # headers.contentType = 'text/plain'
    bucketName = os.getenv("OBS_BUCKET")
    # 对象名，即上传后的文件名
    objectKey = "QUWAN_DATA/Vietnam/debug/test.txt"
    # 待上传文件/文件夹的完整路径，如aa/bb.txt，或aa/
    file_path = 'download/test.txt'
    # 上传文件的自定义元数据
    # metadata = {'meta1': 'value1', 'meta2': 'value2'}
    # 文件上传
    resp = obsClient.putFile(bucketName, objectKey, file_path=file_path, metadata=None, headers=headers)
    # 返回码为2xx时，接口调用成功，否则接口调用失败
    if resp.status < 300:
        print('Put File Succeeded')
        print('requestId:', resp.requestId)
        print('etag:', resp.body.etag)
        print('versionId:', resp.body.versionId)
        print('storageClass:', resp.body.storageClass)
    else:
        print('Put File Failed')
        print('requestId:', resp.requestId)
        print('errorCode:', resp.errorCode)
        print('errorMessage:', resp.errorMessage)
except:
    print('Put File Failed')
    print(traceback.format_exc())

finally:
    # 关闭obsClient
    obsClient.close()
