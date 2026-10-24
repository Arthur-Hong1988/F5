from IPy import IPSet, IP
import re
import sys


def regiondict(file):
    dictv4 = {}
    dictv6 = {}
    province = ""
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "gtm" in line:
                # gtm region /Common/CN_AnHui_CMCC {
                province = line.split(' ')[2].split('/')[2]
                subnetv4 = []
                subnetv6 = []
                dictv4[province] = subnetv4
                dictv6[province] = subnetv6
            if "subnet" in line:
                # subnet 36.161.0.0/16 { }
                net = re.sub(' +', ' ', line).strip().split(' ')[1]
                if IP(net).version() == 4:
                    subnetv4.append(net)
                elif IP(net).version() == 6:
                    subnetv6.append(net)
            dictv4[province] = subnetv4
            dictv6[province] = subnetv6
    return dictv4, dictv6


def combine(olddictv6, newdictv4):
    # ###########################################
    # 【老地址库】            【新地址库】
    # 电信：CN_AnHui_CTC       ctc-anhui
    # 联通：CN_AnHui_CNC       cnc-anhui
    # 移动：CN_AnHui_CMCC      cmnet-anhui
    # 铁通：CN_AnHui_Other     crtc-anhui
    # ##################【特殊情况】##############
    # 【山西 太原】
    # CN_ShanXi_TY_CMCC       cmcc-shanxi
    # CN_ShanXi_TY_CNC        cnc-shanxi
    # CN_ShanXi_TY_CTC        ctc-shanxi
    # CN_ShanXi_TY_Other      other-shanxi
    # 【陕西 西安】
    # CN_ShanXi_XA_CMCC       cmcc-shannxi
    # CN_ShanXi_XA_CNC        cnc-shannxi
    # CN_ShanXi_XA_CTC        ctc-shannxi
    # CN_ShanXi_XA_Other      other-shannxi
    # 以上述对应关系将新v4地址库地址添加到老地址库对应运营商的对应省份中
    # ###########################################

    for k1, v1 in olddictv6.items():
        if 'ShanXi' in k1:
            isp1 = k1.split('_')[3].lower()
        else:
            isp1 = k1.split('_')[2].lower()
        p1 = k1.split('_')[1].lower()

        for k2, v2 in newdictv4.items():
            isp2 = k2.split('-')[0].lower()
            p2 = k2.split('-')[1].lower()
            if isp1 == isp2 and 'ShanXi_TY' in k1 and p2 == 'shanxi':
                olddictv6[k1].extend(v2)
            elif isp1 == isp2 and 'ShanXi_XA' in k1 and p2 == 'shannxi':
                olddictv6[k1].extend(v2)
            elif isp1 == isp2 and p1 == p2:
                olddictv6[k1].extend(v2)
    return olddictv6


def filemerge(d):
    with open('result.txt', 'w') as f:
        for k8, v8 in d.items():
            f.write('gtm region /Common/%s {\n' % k8)
            f.write('    region-members {\n')
            for vv in v8:
                vvv = str(vv)
                f.write('        subnet %s { }\n' % vvv)
            f.write('    }\n')
            f.write('}\n')
    f.close()


if __name__ == "__main__":
    v6dict = regiondict('bigip_gtm.txt')[1]
    v4dict = regiondict('IPv4 Region.txt')[0]
    d = combine(v6dict, v4dict)
    filemerge(d)
    for k3, v3 in d.items():
        if len(v3) == 0:
            print(k3)





