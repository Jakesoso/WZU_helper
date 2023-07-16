import binascii
from pyDes import ECB, PAD_PKCS5, des


def des_encrypt(s, key):
    """
    DES 加密
    :param key: 秘钥
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = key
    k = des(secret_key, mode=ECB, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return en  # 得到加密后的16位进制密码 <class 'bytes'>


def encrypt(pd, key):
    """
    密码加密过程：
    1 从认证页面中可获得base64格式的秘钥
    2 将秘钥解码成bytes格式
    3 输入明文密码
    4 通过des加密明文密码
    5 返回base64编码格式的加密后密码
    :param pd: 明文密码
    :param key: 秘钥
    :return: 加密后的密码（base64格式）
    """
    key = binascii.a2b_base64(key.encode('utf-8'))  # 先解码 <class 'bytes'>
    pd_bytes = des_encrypt(pd, key)  # 得到加密后的16位进制密码 <class 'bytes'>
    pd_base64 = binascii.b2a_base64(pd_bytes, newline=False).decode('utf-8')
    return pd_base64
