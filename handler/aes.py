# from utils.tool import load_cfg
# from utils.config import Config
# config = Config()
# config.load_cfg("conf/config.json")
# cfg = config.cfg

from os import getenv
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def aes_encrypt(key, data):
    key = hex_to_bytes(key)
    data = data.encode("utf-8")
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    return bytes_to_hex(iv + encrypted_data)


def aes_decrypt(key, encrypted_data):
    key = hex_to_bytes(key)
    encrypted_data = hex_to_bytes(encrypted_data)
    iv = encrypted_data[: AES.block_size]
    encrypted_data = encrypted_data[AES.block_size :]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode("utf-8")


def bytes_to_hex(data):
    return "".join(f"{byte:02X}" for byte in data)


def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)


def decrypt_url(url):
    # DECRYPT_KEY = cfg["common"]["DECRYPT_KEYs"]
    DECRYPT_KEY = getenv("DECRYPT_KEY")
    if len(DECRYPT_KEY) != 32:
        raise ValueError("DECRYPT_KEY is empty or not 32 characters long")

    # Decrypt the URL
    try:
        r = aes_decrypt(DECRYPT_KEY, url)
    except ValueError:
        raise ValueError(
            "Fail to decrypt url, DECRYPT_KEY might be wrong, please check."
        )
    return r


if __name__ == "__main__":

    key = bytes_to_hex(get_random_bytes(16))
    data = "Hello, AES!"

    print("Key:", key)

    encrypted_data = aes_encrypt(key, data)
    print("Encrypted:", encrypted_data)

    decrypted_data = aes_decrypt(key, encrypted_data)
    print("Decrypted:", decrypted_data)
