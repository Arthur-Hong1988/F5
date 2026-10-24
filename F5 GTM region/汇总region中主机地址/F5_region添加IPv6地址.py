# Edit by Arthur
from IPy import IPSet, IP
import re
import sys


def getaddrdic():
    olddict = {}
    newdict = {}
    oldprovince = ""
    newprovince = ""

    with open('bigip_gtm.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "gtm" in line:
                oldprovince = line.split(' ')[2].split('/')[2]
                oldsubnet = []
                olddict[oldprovince] = oldsubnet
            if "subnet" in line:
                oldnet = re.sub(' +', ' ', line).strip().split(' ')[2]
                v4dict[v4province].append(v4net)

    with open('IPv6_Region.txt', 'r') as ff:
        Lines = ff.readlines()
        for Line in Lines:
            if "gtm" in Line:
                v6province = Line.split(' ')[2].split('/')[2]
                v6subnet = []
                v6dict[v6province] = v6subnet
            if "subnet" in Line:
                v6net = re.sub(' +', ' ', Line).rstrip().split(' ')[2]
                v6dict[v6province].append(v6net)

    # fff = open("v4dict.txt", 'w')
    # sys.stdout = fff
    # print(v4dict)

    # ffff = open("v6dict.txt", 'w')
    # sys.stdout = ffff
    # print(v6dict)

    # for v4k, v4v in v4dict.items():
    #    print(v4k)

    # for v6k, v6v in v6dict.items():
    #    print(v6k)

    for v4k, v4v in v4dict.items():
        v4p = v4k.split('_')[1]      # 省份 AnHui
        lowp = v4p.lower()           # 省份小写 anhui
        sxp = ''                     # 省份小写缩写 ah
        vendor = v4k.split('_')[2]   # 运营商
        for i in v4p:
            if i.isupper() == 1:
                sxp += i              # 得到大写的省份的缩写，例如原来AnHui就得到AH
                sxp = sxp.lower()

        for v6k, v6v in v6dict.items():
            v6p = v6k.split('_')[1]
            if "cms" in v6k and vendor == "CMCC" and (v6p == lowp or v6p == sxp):
                v4v.extend(v6v)
            if "ctc" in v6k and vendor == "CTC" and (v6p == lowp or v6p == sxp):
                v4v.extend(v6v)
            if "cuc" in v6k and vendor == "CNC" and (v6p == lowp or v6p == sxp):
                v4v.extend(v6v)

    # v46 = open("v46dict.txt", 'w')
    # sys.stdout = v46
    # print(v4dict)

    with open('final46.txt', 'w') as f1:
        for k1, v1 in v4dict.items():
            f1.write('gtm region /Common/%s {\n' % k1)
            f1.write('    region-members {\n')
            for vv in v1:
                vvv = str(vv)
                f1.write('        subnet %s { }\n' % vvv)
            f1.write('    }\n')
            f1.write('}\n')
    f1.close()


if __name__ == "__main__":
    getaddrdic()

