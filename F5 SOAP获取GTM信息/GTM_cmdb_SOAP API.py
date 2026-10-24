import json
import sys
import bigsuds
import re
import xlrd
import time
import xlsxwriter
import xlwt
import socket
import os
import datetime
import sys
import threading
import requests
from queue import Queue
reload(sys)
sys.setdefaultencoding('gb2312')
requests.packages.urllib3.disable_warnings()

# This script is used for adding LangFang poolmember for all wideips#
class restapi():
    def __init__(self,username="admin",password="Ad@1hblsqt"):
        self.username = username
        self.password = password
        
        #get fqdns that contains lui-hk or lu-global
    def getserverdcip(self):
        server_dc_list = []
        url = "https://30.95.0.33/mgmt/tm/gtm/server"
        resp = requests.get(url, auth=(self.username, self.password), verify=False).json()
        for item in resp["items"]:
            dict = {}
            server = item["name"]
            dc = item["datacenter"]
            ip = item["addresses"][0]["name"]
            dict["server"] = server
            dict["dc"] = dc
            dict["ip"] = ip
            server_dc_list.append(dict)
        #print(server_dc_list)
        #[{'ip': u'101.227.100.177', 'dc': u'/Common/SH_BX_CTC', 'server': u'lutest_101_227_100_177'}]
        return server_dc_list


class SOAP():
    def __init__(self,serverdcip,hostname='30.95.0.34',username="admin",password="Ad@1hblsqt"):
        self.serverdcip = serverdcip
        self.hostname = hostname
        self.username = username
        self.password = password

    def getapi(self):
        api = bigsuds.BIGIP(self.hostname,username=self.username,password=self.password)
        return api

    def getwideips(self):
        api = self.getapi().GlobalLB
        v4 = api.WideIPV2.get_list_by_type(['GTM_QUERY_TYPE_A'])[0]
        v6 = api.WideIPV2.get_list_by_type(['GTM_QUERY_TYPE_AAAA'])[0]
        v4.extend(v6)
        wideips = v4
        #print(wideips)
        #[{'wideip_type': 'GTM_QUERY_TYPE_A', 'wideip_name': '/Common/mk.pacfc.com'}, {'wideip_type': 'GTM_QUERY_TYPE_A', 'wideip_name': '/Common/wrmp-dr.phrzdb.com'},...]

        memberstate = []
        for wideip in wideips:
            pool = api.WideIPV2.get_wide_ip_pool([wideip]) 
            #print(pool)
            #[[{'pool_type': 'GTM_QUERY_TYPE_A', 'pool_name': '/Common/Pool_mk_pacfc_com'}]]
            if pool[0][0]["pool_type"] == "GTM_QUERY_TYPE_A":
                wideip["wideip_type"] = "A"
            elif pool[0][0]["pool_type"] == "GTM_QUERY_TYPE_AAAA":
                wideip["wideip_type"] = "AAAA"
            wideipname = wideip["wideip_name"].split('/',2)[2]
            members = api.PoolV2.get_member(pool[0])
            #print(members)
            #[[{'name': 'SZ_Puhui_202_69_31_48_BGP_443', 'server': '/Common/SZ_Puhui_202_69_31_48_BGP'}, {'name': 'SZ_Puhui_43_230_223_14_BGP_443', 'server': '/Common/SZ_Puhui_43_230_223_14_BGP'}]]
            memberstate = api.PoolV2.get_member_enabled_state(pool[0],members)
            #print(memberstate)
            #[['STATE_ENABLED', 'STATE_ENABLED']]

            if len(members[0]) >= 2:
                redundancy = "True"
            else:
                redundancy = "False"

            datacenter = ''
            ip = ''
            for member in members[0]:
                server = member["server"].split('/',2)[2]
                for item in self.serverdcip:
                    #[{'ip': u'101.227.100.177', 'dc': u'/Common/SH_BX_CTC', 'server': u'lutest_101_227_100_177'}]
                    if item["server"] == server:
                        datacenter = item["dc"].split('/',2)[2]
                        ip = item["ip"]
                    else:
                        continue
                #datacenter = api.Server.get_data_center([server])[0].split('/',2)[2]
                #ip = api.Server.get_ip_v2([server])[0][0]["addresses_on_device"][0]
                memberindex = members[0].index(member)
                if memberstate[0][memberindex] == "STATE_ENABLED":
                    state = "up"
                elif memberstate[0][memberindex] == "STATE_DISABLED":
                    state = "down"
                member["state"]=state
                member["DC"] = datacenter
                member["ip"] = ip
                del member["name"]
                del member["server"]
                #print(member)
                #{'DC': ['/Common/SG_KJ_Singtel'], 'IP': '203.208.157.5', 'name': 'SG_KJ_203_208_157_5_Singtel_80', 'server': '/Common/SG_KJ_203_208_157_5_Singtel'}
            #print(members)
            wideip["members"] = members[0]
            wideip["redundancy"] = redundancy
            wideip["wide_ip"] = wideipname
            wideip["rrs_type"] = "wideip"
            wideip["net_type"]="domain2"
            del wideip["wideip_name"]
        #print(wideips)
        #[{'redundancy': 'True', 'net_type': 'domain2', 'members': [{'DC': u'SH_BX_CTC', 'ip': u'101.89.64.39', 'state': 'STATE_ENABLED'}, {'DC': u'SH_BX_CNC', 'ip': u'103.36.174.89', 'state': 'STATE_ENABLED'}, {'DC': u'SH_WGQ_CTC', 'ip': u'101.227.60.7', 'state': 'STATE_ENABLED'}, {'DC': u'SH_WGQ_CNC', 'ip': u'139.227.231.25', 'state': 'STATE_ENABLED'}], 'rrs_type': 'wideip', 'wide_ip': 'www.lu-tech.cn', 'wideip_type': 'A'}]
        return wideips


    def getzonefiles(self):
        # get all zoneviews
        api = self.getapi().Management
        zone_view = ['external']
        zonenames = api.Zone.get_zone_name(zone_view)
        #print(zonenames)
        #[{'zone_name': 'lufax.com.', 'view_name': 'external'}, {'zone_name': 'lu.com.', 'view_name': 'external'},...]

        # use given zonename to get all rrs
        os.chdir(path)
        for zone in zonenames: 
            if "arpa" not in zone['zone_name']:
                output = api.ResourceRecord.get_rrs([zone])
                with open(zone['zone_name']+'txt','w') as f:
                    for rr in output[0]:
                        if (' A ' or ' AAAA ') in rr and '600' in rr:
                            f.write(rr + '\n')
            else:
                continue
            f.close()
    

    def getzonerunners(self):
        rrslist = []
        file_name_list = os.listdir(path)
        #file_name_list = ['palubao.com.txt']
        #print(file_name_list)
        #['palubao.com.txt', 'lujsclub.com.txt', 'cqfae.com.txt', ...]
        for filename in file_name_list:
            with open('%s/%s' % (path,filename),'r') as ff:
                lines = ff.readlines()
                for line in lines:
                    if "101.227.100.177" not in line:
                        memberlist = []
                        members = {}
                        rrs = {}
                        line = re.sub(' +',' ',line).rstrip()
                        wideip = line.split(' ')[0]
                        type = line.split(' ')[3]
                        ip = line.split(' ')[4]
                        rrs['wide_ip'] = wideip
                        rrs['wideip_type'] = type
                        members["DC"] = "N/A"
                        members["ip"] = ip
                        members['state'] = 'up'
                        memberlist.append(members)
                        rrs["members"] = memberlist
                        rrs['redundancy'] = 'False'
                        rrs["rrs_type"] = "zonerunner"
                        rrs["net_type"]="domain2"
                        rrslist.append(rrs)

        dict = {}
        for item in rrslist:
            domain = item.get('wide_ip')
            if domain in dict:
                dict[domain].get('members').extend(item.get('members'))
                dict[domain]['redundancy'] = 'True'
            else:
                dict[domain] = item
        newlist = []
        newlist = dict.values()
        #print(newlist)
        return newlist


#        bak = rrslist
#        for item1 in rrslist:
#            for item2 in bak: 
#                if rrslist.index(item1) != bak.index(item2) and item1["wide_ip"] == item2["wide_ip"]:
#                    item1["members"].extend(item2["members"])
#                    item1["redundancy"] = "True"
#                else:
#                    continue
#        #print(rrslist)
#        return rrslist


def sendsyslog(message):
    message = json.dumps(message)
    format="%Y-%m-%d %H:%M:%S"     
    t = time.strftime(format,time.localtime(time.time())) #2022-10-12 08:46:23

    FACILITY = {'daemon':3,'local0':16}
    LEVEL = {'info':6,'debug':7}
    level=LEVEL['info']
    facility=FACILITY['daemon']
    host='30.94.0.169'
    port=514

    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    data = '<%d>%s'%(level+facility*8,message)
    sock.sendto(data,(host,port))
    sock.close()


def redundancycheck(wideips):
    yesterday = time.strftime('%Y%m%d', time.localtime(time.time()-86400))
    logpath = "/wls/networkdaily/networkdaily/ribao/getlog/log_%s/gtm_redundancycheck.log" %yesterday
    t1 = time.strftime('%m%d',time.localtime(time.time())) #1012
    f_res = open(logpath,"wb")
    f_res.write("GTM name resolved inequivalent in DCs:\n")
    for item in wideips:
        if 'test' not in item["wide_ip"] and 'stg' not in item["wide_ip"] and item["redundancy"] == 'False':
            f_res.write(item["wide_ip"] + '-' + item["members"][0]["ip"] + '-' + item["rrs_type"] + "\n")
        else:
            continue
    f_res.close()



if __name__ == "__main__": 
    starttime = datetime.datetime.now()
    path = "/home/wls81opr/zonefile"
    b = restapi()
    serverdcip = b.getserverdcip()
    
    a = SOAP(serverdcip)
    a.getzonefiles()
    zonerunners = a.getzonerunners()

    wideips = a.getwideips()
    wideips.extend(zonerunners)
    #print(wideips)
    #{'redundancy': 'True', 'net_type': 'domain2', 'members': [{'DC': u'LF_CUCC_CNC', 'IP': u'120.52.138.14'}, {'DC': u'SH_BX_CTC', 'IP': u'101.89.64.51'}, {'DC': u'SH_BX_CNC', 'IP': u'103.36.174.91'}, {'DC': u'SH_BX_BaiDuCloud', 'IP': u'183.131.207.53'}, {'DC': u'SH_WGQ_CTC', 'IP': u'101.227.60.19'}, {'DC': u'SH_WGQ_CNC', 'IP': u'139.227.231.27'}], 'rrs_type': 'wideip', 'wide_ip': 'www.lu.com', 'wideip_type': 'A'}]
    for message in wideips:
        for member in message["members"]:
            newdict = {}
            newdict["wide_ip"] = message["wide_ip"]
            newdict['wideip_type'] = message["wideip_type"]
            newdict["DC"] = member["DC"]
            newdict["ip"] = member["ip"]
            newdict['redundancy'] = message["redundancy"]
            newdict["state"] = member["state"]
            newdict["rrs_type"] = message["rrs_type"]
            newdict["net_type"]="domain2"
            #print(newdict)
            sendsyslog(newdict)
    endtime = datetime.datetime.now()
    print((endtime-starttime).seconds)
    redundancycheck(wideips)   





