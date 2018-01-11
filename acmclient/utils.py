# coding: utf-8
import re
import hmac
import base64
import hashlib
from hashlib import sha1


REG_VALID_CHAR = r"^[\w\.\-\:]+$"

def check_param_isvalid(value: str) -> bool:
    """检查参数是否合法

    :param value: 参数值
    :return: Boolean
    """
    return re.match(REG_VALID_CHAR, value)

def check_dataId(dataId):
    """检查DataId是否合法

    :param dataId:
    :return:
    """
    return check_param_isvalid(dataId)

def check_group(group):
    """

    :param group:
    :return:
    """
    return check_param_isvalid(group)

def get_md5_string(value):
    """

    :param value:
    :return:
    """
    if not value:
        return ""
    m = hashlib.md5()
    m.update(value.encode('gbk'))
    return m.hexdigest()

def HmacSHA1Encrypt(encryptText: str, encryptKey: str) -> str:
    """

    :param encryptText:
    :param encryptKey:
    :return:
    """
    encryptText = bytes(encryptText, 'UTF-8')
    encryptKey = bytes(encryptKey, 'UTF-8')
    my_sign = hmac.new(encryptKey, encryptText, sha1).digest()
    my_sign = base64.b64encode(my_sign)
    return str(my_sign, 'UTF-8')


