# coding: utf-8

import os

import pytest

from acmclient import ACMClient

ACM_ACCESS_KEY_ENV = "ACM_ACCESS_KEY"
ACM_SECRET_KEY_ENV = "ACM_SECRET_KEY"
ACM_ENDPOINT_ENV = "ACM_ENDPOINT"
ACM_NAMESPACE_ENV = "ACM_NAMESPACE_ENV"

acm_client = None

@pytest.fixture(scope="session")
def config():
    assert os.environ.get(ACM_ACCESS_KEY_ENV), "[AcmClient] options.accessKey is required"
    assert os.environ.get(ACM_SECRET_KEY_ENV), "[AcmClient] options.secretKey is required"
    assert os.environ.get(ACM_ENDPOINT_ENV), '[AcmClient] options.endpoint is required'
    assert os.environ.get(ACM_NAMESPACE_ENV), '[AcmClient] options.namespace is required'
    return {"endpoint": os.environ[ACM_ENDPOINT_ENV], "namespace": os.environ[ACM_NAMESPACE_ENV],
            "accesskey": os.environ[ACM_ACCESS_KEY_ENV], "secretkey": os.environ[ACM_SECRET_KEY_ENV]}

@pytest.fixture(scope="session")
def acmclient(config):
    global acm_client
    if not acm_client:
        acm_client = ACMClient(**config)
    return acm_client
