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
    acm_client = ACMClient(endpoint="xxx", namespace="xxx", accesskey="xxx", secretkey="xxx")
    acm_client.getconfig(data_id="xxx", group="xxx")
    acm_client.subscribe(data_id="xxx", group="xxx")

if __name__ == "__main__":
    main()
```