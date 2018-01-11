# coding: utf-8
import random
import time
import requests


import acmclient.const as Constants
from .utils import (
    check_dataId, check_group, HmacSHA1Encrypt,
    get_md5_string
)

GET_CONFIG_SUFFIX = SUBSCRIBE_SUBFFIX = '/config.co'


class ServerListManager(object):
    _server_list_cache = dict()
    _current_server_ip = None


    def get_current_server_ip(self):
        if not self._current_server_ip:
            self._current_server_ip = self.get_unit_address()
        return self._current_server_ip

    def get_current_unit(self):
        pass

    def get_unit_address(self, unit=Constants.CURRENT_UNIT) -> str:
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

    def fetch_server_list(self, unit):
        res = requests.get(self.request_server_list_url(unit))
        if not res.text:
            raise ValueError("[diamond#ServerListManager] Diamond return empty hosts")
        hosts = res.text.split('\n')
        hosts.remove('')
        return hosts

    def request_server_list_url(self, unit):
        if unit == Constants.CURRENT_UNIT:
            return f"http://{self.endpoint}:8080/diamond-server/diamond"
        else:
            return f"http://{self.endpoint}:8080/diamond-server/diamond-unit-{unit}?nofix=1"


class ACMClient(ServerListManager):
    """ACM client
    """

    _config_content = None
    _is_long_pulling = False
    _isClose = False


    def __init__(self, endpoint: str, namespace: str, accesskey: str, secretkey: str):
        """初始化阿里应用配置管理

        :param endpoint:
        :param namespace:
        :param accesskey:
        :param secretkey:
        """
        assert endpoint, '[AcmClient] options.endpoint is required'
        assert namespace, '[AcmClient] options.namespace is required'
        assert accesskey, '[AcmClient] options.accessKey is required'
        assert secretkey, '[AcmClient] options.secretKey is required'
        self.endpoint = endpoint
        self.namespace = namespace
        self._accesskey = accesskey
        self._secretkey = secretkey


    def getconfig(self, dataId: str, group: str, **kwargs) -> str:
        """获取配置

        :param dataId: id of the data
        :param group: group name of the data
        :param kwargs:
        :return: value
        """
        assert check_dataId(dataId), f'[dataId] only allow digital, ' \
                                     f'letter and symbols in [ "_", "-", ".", ":" ], but got {dataId})'
        assert check_group(group), f'[group] only allow digital, ' \
                                   f'letter and symbols in [ "_", "-", ".", ":" ], but got {group}'
        self.dataId = dataId
        self.group = group
        headers = self._get_request_header()
        url = self.get_request_url(GET_CONFIG_SUFFIX)
        params = {
            "tenant": self.namespace,
            "dataId": dataId,
            "group": group
        }
        try:
            res = requests.get(url, headers=headers, params=params, verify=False)
        except:
            raise
        else:
            print(res.text)
            self._config_content = res.text
        return res.text

    def subscribe(self, dataId: str, group: str, **kwargs) -> bool:
        assert check_dataId(dataId), f'[dataId] only allow digital, ' \
                                     f'letter and symbols in [ "_", "-", ".", ":" ], but got {dataId})'
        assert check_group(group), f'[group] only allow digital, ' \
                                   f'letter and symbols in [ "_", "-", ".", ":" ], but got {group}'
        self.dataId = dataId
        self.group = group
        self._isClose = True
        self._start_long_pulling()


    def _check_server_config_info(self):
        headers = self._get_request_header(longPullingTimeout="30000")
        post_data = self.get_subscribe_post_data(self.dataId, self.group)
        url = self.get_request_url(SUBSCRIBE_SUBFFIX)
        try:
            res = requests.post(url, headers=headers, data=post_data, verify=False, timeout=40)
        except:
            raise
        else:
            if res.text:
                self.getconfig(self.dataId, self.group)

    def unsubscribe(self):
        self._isClose = False

    def _start_long_pulling(self):
        """

        :return:
        """
        if self._is_long_pulling:
            return

        self._is_long_pulling = True
        while self._isClose:
            try:
                self._check_server_config_info()
            except:
                raise

        self._is_long_pulling = False



    def get_subscribe_post_data(self, dataId: str, group: str) -> dict:
        md5_content = get_md5_string(self._config_content)
        data = Constants.WORD_SEPARATOR.join([dataId, group, md5_content, self.namespace])
        data += Constants.LINE_SEPARATOR
        return {"Probe-Modify-Request": data}

    def get_request_url(self, path, ssl=False):
        if ssl:
            return f"https://{self._current_server_ip}:443/diamond-server{path}"
        return f"http://{self._current_server_ip}:8080/diamond-server{path}"


    def get_spas_signature(self, group: str, millis: int) -> str:
        signStr = "+".join([self.namespace, group, str(millis)])
        return HmacSHA1Encrypt(signStr, self._secretkey)


    def _get_request_header(self, **kwargs):
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
