# # -*- coding=utf-8
# from utils.tool import load_cfg
# from utils.logger import init_logger
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client
# import os

# cfg = load_cfg(".\\config\\config_xyh.json")
# logger = init_logger("cos_sdk")

# # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成    
# secret_id = cfg["cos"]["secret_id"] # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
# secret_key = cfg["cos"]["secret_key"] # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
# cos_region = 'ap-beijing'   # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
#                             # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
# token = None                # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
# scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

# config = CosConfig(Region=cos_region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
# client = CosS3Client(config)
# logger.info(
#     "cos init  client succeed. %s", client.get_conf().get_host(Bucket=cfg["cos"]["bucket"])
# )

# # 高级上传接口（推荐）
# def upload_file(from_path:str, to_path:str)->str:
#     '''cos上传接口:根据文件大小自动选择简单上传或分块上传,分块上传具备断点续传功能'''
#     if not os.path.exists(from_path):
#         logger.error(f"cos upload_file error, not such file {from_path}")
#         raise FileNotFoundError
#         # return ""
#     # base = os.path.basename(from_path)
#     base = os.path.basename(to_path) #{vid}.m4a
#     cos_path = os.path.join(cfg["cos"]["save_path"], base)
#     cos_link = cfg["cos"]["url_base"] + cos_path
#     response = client.upload_file(
#         Bucket=cfg["cos"]["bucket"],
#         # LocalFilePath='local.txt',
#         LocalFilePath=from_path,
#         # Key='/QUWAN_DATA/xyh/local.txt',
#         Key=cos_path,
#         PartSize=1,
#         MAXThread=10,
#         EnableMD5=False
#     )
#     logger.info(f"cos upload_file done, local_file_path:{from_path} cos_link:{cos_link} cos_path:{cos_path} file_id:{response['ETag']}")
#     return cos_link