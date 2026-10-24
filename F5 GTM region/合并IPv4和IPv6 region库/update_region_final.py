from IPy import IPSet, IP
import re
import sys


class UpdateRegion(object):
    def __init__(self, file):
        self.file = file

    def regiondic(self):
        regdictv4 = {}      # 省份：v4地址段
        regdictv6 = {}      # 省份：v6地址段
        province = ""
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                strlist = ['all', 'cernet', 'china']
                if "gtm" in line:
                    province = line.split(' ')[2].split('/')[2]    # CN_AnHui_CMCC
                    subnetv4 = []
                    subnetv6 = []
                    regdictv4[province] = subnetv4
                    regdictv6[province] = subnetv6
                if "subnet" in line:
                    prefixlist = ['30', '31', '32']
                    net = re.sub(' +', ' ', line).strip().split(' ')[1]                # 36.161.0.0/16
                    # 判断网络前缀是否为30 31 32，为了v6地址可能也会有30 31 32的前缀，所以需要同时判断为v4地址
                    if net.split('/')[1] in prefixlist and (IP(net).version() == 4):
                        net = net.split('.')[0] + '.' + net.split('.')[1] + '.' + net.split('.')[2] + '.' + '0/24'
                        ipnet = IP(net)
                        subnetv4.append(ipnet)
                    elif IP(net).version() == 6:
                        subnetv6.append(net)
                    else:
                        ipnet = IP(net)
                        subnetv4.append(ipnet)
                regdictv4[province] = subnetv4
                regdictv6[province] = subnetv6
        return regdictv4, regdictv6


    # def addrmerge(self):
    #     dic = UpdateRegion.regiondic(self)
    #     dicv4 = dic[0]
    #     dicv6 = dic[1]
    #     for k, v in dic.items():
    #         subnet4 = []
    #         subnet6 = []
    #         for netaddr in v:
    #             list = []
    #             if netaddr.version() == 4:
    #                 subnet4.append(netaddr)
    #             if netaddr.version() == 6:
    #                 subnet6.append(netaddr)
    #         a = IPSet(subnet4)
    #         for aa in a:
    #             list.append(aa)
    #         dic[k] = list+subnet6
    #     return dic
    #
    # def filemerge(self):
    #     R = UpdateRegion.addrmerge(self)
    #     with open('result.txt', 'w') as ff:
    #         for k1, v1 in R.items():
    #             ff.write('gtm region /Common/%s {\n' % k1)
    #             ff.write('    region-members {\n')
    #             for vv in v1:
    #                 vvv = str(vv)
    #                 ff.write('        subnet %s { }\n' % vvv)
    #             ff.write('    }\n')
    #             ff.write('}\n')
    #     ff.close()


if __name__ == "__main__":
    oldv4 = UpdateRegion('bigip_gtm.txt').regiondic()[0]
    # ff = open("oldv4.txt", 'w')
    # sys.stdout = ff
    # print(oldv4)

    newv4 = UpdateRegion('IPv4 Region.txt').regiondic()[0]
    # fff = open("newv4.txt", 'w')
    # sys.stdout = fff
    # print(newv4)

    for kk, vv in oldv4.items():
        oldp = kk.split('_')[1].lower()     # CN_AnHui_CMCC切片得到AnHui
        oldISP = kk.split('_')[2].lower()  # CN_AnHui_CMCC切片得到CMCC
        for kkk, vvv in newv4.items():
            newp = kkk.split('-')[1]  # cmnet-anhui切片得到anhui
            newISP = kkk.split('-')[0]  # cmnet-anhui切片得到cmnet
            if set(vv) & set(vvv):
                print(oldp + '---' + newp)

    a = [IP("1.1.1.0/24"), IP("2.2.2.0/24")]
    b = [IP("1.1.1.0/24")]
    c = set(a) & set(b)
    print(c)
