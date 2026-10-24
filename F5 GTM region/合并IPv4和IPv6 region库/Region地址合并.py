# Edit by Arthur
from IPy import IPSet, IP
import re
import sys


def getaddrdic(file):
    dict = {}
    province = ""

    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "gtm" in line:
                province = line.split(' ')[2].split('/')[2]
                subnet = []
                dict[province] = subnet
            if "subnet" in line:
                net = re.sub(' +', ' ', line).strip().split(' ')[1]
                dict[province].append(net)

    fff = open("olddict.txt", 'w')
    sys.stdout = fff
    print(dict)

    ffff = open("oldp.txt", 'w')
    sys.stdout = ffff
    for k, v in dict.items():
       print(k)


def addrmerge(file1, file2):
    olddic = getaddrdic(file1)
    newdic = getaddrdic(file2)
    for oldk, oldv in olddic.items():
        oldp = oldk.split('_')[1]      # 省份 AnHui
        lowp = oldp.lower()            # 省份小写 anhui
        sxp = ''                       # 省份小写缩写 ah
        vendor = oldk.split('_')[2]    # 运营商
        for i in oldp:
            if i.isupper() == 1:
                sxp += i              # 得到大写的省份的缩写，例如原来AnHui就得到AH
                sxp = sxp.lower()
        # cmcc包含cmnet、crtc
        # cnc
        # ctc
        # cernet
        for newk, newv in newdic.items():
            newp = newk.split('_')[1]
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
    getaddrdic('bigip_gtm.txt')

