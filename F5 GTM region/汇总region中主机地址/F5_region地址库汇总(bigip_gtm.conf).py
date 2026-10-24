from IPy import IPSet, IP
import re
import sys


def region():
    regdict = {}
    province = ""
    # 将region中的信息以字典形式存储，key为省份，value为subnet处于一个列表
    with open('region.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "gtm" in line:
                province = line.split(' ')[2].split('/')[2]
                # print(province)
                subnet = []
                regdict[province] = subnet
            if "subnet" in line:
                net = re.sub(' +', ' ', line).rstrip().split(' ')[2]
                if '/32' in net.split('.')[3]:
                    net = net.split('.')[0] + '.' + net.split('.')[1] + '.' + net.split('.')[2] + '.' + '0/24'
                ipnet = IP(net)
                regdict[province].append(ipnet)

    #ff = open("test11.txt", 'w')
    #sys.stdout = ff
    #print(regdict)

    # 做IP地址的汇总，但是/32位地址貌似不能汇总
    for k, v in regdict.items():
        regdict[k] = IPSet(v)
    #ff = open("test22.txt", 'w')
    #sys.stdout = ff
    #print(regdict)

    # 将v4 subnet合并后写入到final2.txt中
    with open('final.txt', 'w') as fff:
        for k1, v1 in regdict.items():
            fff.write('gtm region /Common/%s {\n' % k1)
            fff.write('    region-members {\n')
            for vv in v1:
                vvv = str(vv)
                fff.write('        subnet %s { }\n' % vvv)
            fff.write('    }\n')
            fff.write('}\n')

    fff.close()


if __name__ == "__main__":
    region()


