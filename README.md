# ACM Client
---

## Install
```bash
$ sudo pip3 install acmclient
```

## Getting started


```python
from acmclient import ACMClient

def main():
    acm_client = ACMClient(
        endpoint="acm.aliyun.com",  # acm 控制台查看 如果不是公网， 则需要在对应区域的VPC服务器上运行
        namespace="xxx",  # acm 控制台查看
        accesskey="xxx",  # acm 控制台查看
        secretkey="xxx"  # acm 控制台查看
    )
    acm_client.getconfig(data_id="test", group="DEFAULT_GROUP")
    acm_client.subscribe(data_id="test", group="DEFAULT_GROUP")

    acm_client.unsubscribe()  # 一半情况下不使用

if __name__ == "__main__":
    main()
```