from IPy import IPSet, IP
import re
import sys


class UpdateRegion(object):
    def __init__(self, file):
        self.file = file

    def regiondic(self):
        regdictv4 = {}
        regdictv6 = {}
        province = ""
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "gtm" in line:
                    province = line.split(' ')[2].split('/')[2]
                    # print(province)
                    subnetv4 = []
                    subnetv6 = []
                    regdictv4[province] = subnetv4
                    regdictv6[province] = subnetv6
                if "subnet" in line:
                    prefixlist = ['30', '31', '32']
                    net = re.sub(' +', ' ', line).strip().split(' ')[1]
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

    def addrmerge(self):
        dic = UpdateRegion.regiondic(self)
        dicv4 = dic[0]
        dicv6 = dic[1]
        for k, v in dic.items():
            subnet4 = []
            subnet6 = []
            for netaddr in v:
                list = []
                if netaddr.version() == 4:
                    subnet4.append(netaddr)
                if netaddr.version() == 6:
                    subnet6.append(netaddr)
            a = IPSet(subnet4)
            for aa in a:
                list.append(aa)
            dic[k] = list+subnet6
        return dic

    def filemerge(self):
        R = UpdateRegion.addrmerge(self)
        with open('result.txt', 'w') as ff:
            for k1, v1 in R.items():
                ff.write('gtm region /Common/%s {\n' % k1)
                ff.write('    region-members {\n')
                for vv in v1:
                    vvv = str(vv)
                    ff.write('        subnet %s { }\n' % vvv)
                ff.write('    }\n')
                ff.write('}\n')
        ff.close()


if __name__ == "__main__":
    dics = UpdateRegion()




