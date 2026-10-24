# Edit by Arthur
# 脚本通过F5 GTM的API接口来将特定二级域名相关的所有三级域名的pool中的关于BX和外高桥的节点进行关闭和启用操作

import requests
import json
import sys

# 避免使用request认证的时候报认证风险的日志
requests.packages.urllib3.disable_warnings()


class GtmApi(object):
    def __init__(self, username="admin", password="Ad@1hblsqt"):
        self.username = username
        self.password = password

    # 获取lui-hk或者lu-global相关的所有三级域名wideip所关联的所有pool并放入列表中
    def getpools(self):
        pools = []
        url = "https://30.95.0.33/mgmt/tm/gtm/wideip/a/"
        resp = requests.get(url, auth=(self.username, self.password), verify=False).json()
        for item in resp["items"]:
            poolname = str(item["pools"][0]["name"])
            pools.append(poolname)
        # print(pools)
        return pools

    def addpoolmember(self):
        # 调用getfqdns方法
        poollist = self.getpools()
        # poollist = ['Pool_HK_test']
        param = {"name": "LF_CUCC_124_196_61_0_CTC:LF_CUCC_124_196_61_0_CTC_443"}
        paramdata = json.dumps(param)
        # 要指定header不然会报错
        header = {'Content-Type': "application/json"}
        for pool in poollist:
            url1 = "https://30.95.0.33/mgmt/tm/gtm/pool/a/%s/members" % pool
            resp1 = requests.post(url1, data=paramdata, headers=header, auth=(self.username, self.password), verify=False).json()
            print(resp1)


if __name__ == "__main__":
    t = GtmApi()
    t.addpoolmember()

