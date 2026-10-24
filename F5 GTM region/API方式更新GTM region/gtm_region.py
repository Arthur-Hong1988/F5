# Edit by Arthur 20210824
import requests
import urllib3


def f5_api():
    username = "admin"
    password = "Ad@1hblsqt"
    url = "https://30.95.0.33/mgmt/tm/gtm/region"
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    """
    python 3添加如下代码防止异常报错：
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    python 2添加如下代码防止异常报错：
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    """
    resp = requests.get(url, auth=(username, password), verify=False).json()

    regfile = 'region.txt'
    regdic = {}

    for item in resp["items"]:
        regdic[item["name"]] = [v["name"].split(' ')[-1] for v in item["regionMembers"]]
        """
        regdic[item["name"]] 得到的是name字段的值，即省份
        for v in item["regionMembers"]得到的是
        这样的一个[{"name":"subnet 36.161.0.0/24"},{"name":"subnet 36.161.1.0/24"}]
        v["name"]得到列表中每个字典对应的值，即subnet，然后通过split进行处理。
        """
    print(regdic)

    with open("regfile", 'w') as f:
        f.write(json.dumps(regdic))
    f.close()


if __name__ == "__main__":
    f5_api()
