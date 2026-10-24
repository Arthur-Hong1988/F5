# Edit by Arthur
# 脚本通过F5 GTM的API接口来将特定二级域名相关的所有三级域名的pool中的关于BX和外高桥的节点进行关闭和启用操作

import requests
import json
import sys

# 避免使用request认证的时候报认证风险的日志
requests.packages.urllib3.disable_warnings()


class GtmApi(object):
    def __init__(self, fqdn, username="admin", password="Ad@1hblsqt"):
        self.fqdn = fqdn
        self.username = username
        self.password = password

    # 获取lui-hk或者lu-global相关的所有三级域名wideip所关联的所有pool并放入列表中
    def getfqdns(self):
        pools = []
        url = "https://30.95.0.33/mgmt/tm/gtm/wideip/a/"
        resp = requests.get(url, auth=(self.username, self.password), verify=False).json()
        for item in resp["items"]:
            # 只挑选出和lui-hk或者lu-global相关的域名的pool
            if self.fqdn in item["pools"][0]["name"]:
                poolname = str(item["pools"][0]["name"])
                pools.append(poolname)
        # print(pools)
        return pools

    def setpoolmember(self):
        # 调用getfqdns方法
        poollist = self.getfqdns()
        # 命令行执行python GTM_luHK.py enabled时候获取enabled作为paramdata的参数
        status = sys.argv[1]
        paramdata = {status: True}
        paramdata = json.dumps(paramdata)

        for pool in poollist:
            url1 = "https://30.95.0.33/mgmt/tm/gtm/pool/a/%s/members" % pool
            resp1 = requests.get(url1, auth=(self.username, self.password), verify=False).json()
            for member in resp1["items"]:
                # 针对lui-hk或者lu-global对应pool中的member判断是否存在BX和WGQ的节点vs
                if "BX" in member["name"] or "WGQ" in member["name"]:
                    vsname = member["name"]
                    # url2是获取某个member的api资源的url连接
                    url2 = url1 + "~Common~%s?ver=15.1.2.1" % vsname
                    # 使用patch方法将paramdata参数传到对应的BX或者WGQ资源，并更改属性为paramdata所执行的参数
                    # 开启 {“enabled”:True}
                    # 禁用 {“disabled”:True}
                    resp2 = requests.patch(url2, data=paramdata, auth=(self.username, self.password), verify=False).json()
                    print(resp2)


if __name__ == "__main__":
    luihk = GtmApi("lui-hk")
    luglobal = GtmApi("lu-global")

    setluihk = luihk.setpoolmember()
    setluglobal = luglobal.setpoolmember()

