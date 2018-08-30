# coding: utf-8

import time
import random
import requests

from typing import Optional

from acmclient import const as Constants
from .utils import (
    check_data_id, check_group, hmacsha1_encrypt,
    get_md5_string
)

GET_CONFIG_SUFFIX = SUBSCRIBE_SUBFFIX = '/config.co'


class ServerListManager(object):
    _server_list_cache = dict()
    _current_server_ip = None

    def get_current_server_ip(self):
        """通过endpoint获取ACM 服务器具体IP地址

        :return:
        """
        if not self._current_server_ip:
            self._current_server_ip = self.get_unit_address()
        return self._current_server_ip

    def get_current_unit(self):
        pass

    def get_unit_address(self, unit=Constants.CURRENT_UNIT) -> Optional[str]:
        """获取某个单元的地址

        :return: address
        """
        server_data = self._server_list_cache.get(unit)

        # 不存在则取重新获取一次
        if not server_data:
            server_data = self.fetch_server_list(unit)

            if not server_data:
                return None

            self._server_list_cache[unit] = server_data

        return random.choice(server_data)

    def fetch_server_list(self, unit=Constants.CURRENT_UNIT):
        res = requests.get(self.request_server_list_url(unit))
        if not res.text:
            raise ValueError("[diamond#ServerListManager] Diamond return empty hosts")
        hosts = res.text.split('\n')
        hosts.remove('')
        return hosts

    def request_server_list_url(self, unit=Constants.CURRENT_UNIT):
        if unit == Constants.CURRENT_UNIT:
            return f"http://{self.endpoint}:8080/diamond-server/diamond"
        else:
            return f"http://{self.endpoint}:8080/diamond-server/diamond-unit-{unit}?nofix=1"


class ACMClient(ServerListManager):
    """ACM client
    """

    _config_content = None
    _is_long_pulling = False
    _is_close = False

    def __init__(self, endpoint: str, namespace: str, accesskey: str,
                 secretkey: str, data_id: str = "", group: str = "DEFAULT_GROUP"):
        """ 初始化阿里配置管理

        :param endpoint:
        :param namespace:
        :param accesskey:
        :param secretkey:
        :param data_id:
        :param group:
        """
        assert endpoint, '[AcmClient] options.endpoint is required'
        assert namespace, '[AcmClient] options.namespace is required'
        assert accesskey, '[AcmClient] options.accessKey is required'
        assert secretkey, '[AcmClient] options.secretKey is required'
        self.endpoint = endpoint
        self.namespace = namespace
        self._accesskey = accesskey
        self._secretkey = secretkey
        self.data_id = data_id
        self.group = group

    def getconfig(self, data_id: str, group="DEFAULT_GROUP", **kwargs) -> str:
        """获取配置

        :param data_id: id of the data
        :param group: group name of the data
        :param kwargs:
        :return: value
        """
        assert check_data_id(data_id), f'[data_id] only allow digital, letter and symbols in [ "_", "-", ".", ":" ], but got {data_id})'
        assert check_group(group), f'[group] only allow digital, letter and symbols in [ "_", "-", ".", ":" ], but got {group}'
        self.data_id = data_id
        self.group = group
        headers = self._get_request_header()
        url = self.get_request_url(GET_CONFIG_SUFFIX)
        params = {
            "tenant": self.namespace,
            "dataId": data_id,
            "group": group
        }
        try:
            res = requests.get(url, headers=headers, params=params, verify=False)
        except Exception as e:
            raise e
        else:
            self._config_content = res.text
        return res.text

    def subscribe(self, data_id: str, group="DEFAULT_GROUP", **kwargs) -> bool:
        """通过订阅配置创建长连接

        :param data_id:
        :param group:
        :param kwargs:
        :return:
        """
        assert check_data_id(data_id), f'[data_id] only allow digital, ' \
                                     f'letter and symbols in [ "_", "-", ".", ":" ], but got {data_id})'
        assert check_group(group), f'[group] only allow digital, ' \
                                   f'letter and symbols in [ "_", "-", ".", ":" ], but got {group}'
        self.data_id = data_id
        self.group = group
        self._is_close = True
        self._start_long_pulling()

    def _check_server_config_info(self):
        """检测ACM 服务器端配置是否进行过更改

        :return:
        """
        headers = self._get_request_header(longPullingTimeout="30000")
        post_data = self.get_subscribe_post_data(self.data_id, self.group)
        url = self.get_request_url(SUBSCRIBE_SUBFFIX)
        try:
            res = requests.post(url, headers=headers, data=post_data, verify=False, timeout=40)
        except:
            raise
        else:
            if res.text:
                self.getconfig(self.data_id, self.group)

    def unsubscribe(self):
        """取消订阅， 则不长轮询服务器端

        :return:
        """
        self._is_close = False

    def _start_long_pulling(self):
        """开始长轮询

        :return:
        """
        if self._is_long_pulling:
            return

        self._is_long_pulling = True
        while self._is_close:
            try:
                self._check_server_config_info()
            except:
                raise

        self._is_long_pulling = False

    def get_subscribe_post_data(self, data_id: str, group: str) -> dict:
        """构建订阅数据

        :param data_id:
        :param group:
        :return:
        """
        md5_content = get_md5_string(self._config_content)
        data = Constants.WORD_SEPARATOR.join([data_id, group, md5_content, self.namespace])
        data += Constants.LINE_SEPARATOR
        return {"Probe-Modify-Request": data}

    def get_request_url(self, path, ssl=False):
        """获取请求配置URL

        :param path:
        :param ssl:
        :return:
        """
        if ssl:
            return f"https://{self._current_server_ip}:443/diamond-server{path}"
        return f"http://{self._current_server_ip}:8080/diamond-server{path}"

    def get_spas_signature(self, group: str, millis: int) -> str:
        """获取加密字符串

        :param group:
        :param millis:
        :return:
        """
        signStr = "+".join([self.namespace, group, str(millis)])
        return hmacsha1_encrypt(signStr, self._secretkey)

    def _get_request_header(self, **kwargs):
        """通用请求头设置

        :param kwargs:
        :return:
        """
        if not self._current_server_ip:
            self._current_server_ip = self.get_current_server_ip()
        ts = int(round(time.time() * 1000))
        rt = {
            "Spas-AccessKey": self._accesskey,
            "timeStamp": str(ts),
            'Spas-Signature': self.get_spas_signature(self.group, ts),
        }
        if kwargs:
            rt.update(kwargs)
        return rt
