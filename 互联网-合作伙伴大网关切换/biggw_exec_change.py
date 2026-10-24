#!/usr/bin/env python
#set expandtab
#set shiftwidth=4
#set softtabstop=4
#set tabstop=4
#set backspace=2
#set smarttab
#syntax on
# usage: running in Control node
import os
import sys
import requests
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from big_gateway_switch_network_batch import biggateway_network_switch, checkRoute


headers = {'Content-Type': 'application/json', 'token': '4775b36cfc156ef849ee6c9939da4082'}
#url = 'http://172.23.44.183:23456/api/v3/ci/'
#url = 'http://30.94.0.165:23456/gate/api/v3/ci/'
url = 'http://cmdbv3.devops.lufax.tool/gate/api/v3/ci/'

DNS_INFO_DICT = {}

VS_DICT = {}

NET_NAT_VIP_DICT = {}

NET_NAT_ADDRESS_NAT_DICT = {}


def get_dns_domain(domain, idc):
    print('%sdns_info?domain=%s&q_columns=["domain", "ip", "idc"]'% (url, domain))
    # r = requests.get('%sdns_info?domain=%s&q_columns=["domain", "ip", "idc"]'% (url, domain), headers=headers)
    # result = r.json()['data']
    vip = ''

    result = DNS_INFO_DICT.get(domain, [])

    if result == []:
        print 'dns_info no such domain for domain %s'%domain
        return ''

    if idc is None:
        # return the first vip, for biggw vip in all idc is the same
        # return result[0]['ip']
        vip = result[0]['ip']
    else:
        for re in result:
            if re['idc'] == idc:
                vip = re['ip']
                break
    # if vip is Int will skip routing change
    # r = requests.get('%svs?vip=%s&q_columns=["name", "vip"]'% (url, vip), headers=headers)
    # result = r.json()['data']

    result = VS_DICT.get(vip, [])

    if result == []:
        print 'no such vip %s'%vip
        return ''
    if result[0]['name'].startswith('Int'):
        print 'vip %s has name %s,and will skip it'%(vip, result[0]['name'])
        return ''

    return vip


def get_inbound_vip(snat_in_bound_ip, dest_idc):
    r = requests.get('%snet_nat?source_address_nat=%s&q_columns=["vip", "source_address_nat"]'% (url, snat_in_bound_ip), headers=headers)
    #from ipdb import set_trace; set_trace()
    if r.status_code != 200:
        print 'ERROR: vip %s no SNAT IP!!!'
        return ''
    result = r.json()['data']
    source_address_nat = []
    for re in result:
        vip_tmp = re['vip']
        if dns_vip(dest_idc, vip_tmp):
            #change ip into not dest idc
            if vip_tmp.startswith('30.65'):
                vip_tmp = '30.97.' + vip_tmp.split('.')[2] + '.' + vip_tmp.split('.')[3]
            elif vip_tmp.startswith('30.97'):
                vip_tmp = '30.65.' + vip_tmp.split('.')[2] + '.' + vip_tmp.split('.')[3]
            print 'vip change into %s' % vip_tmp
        source_address_nat.append(vip_tmp)

    return list(set(source_address_nat))

def get_snat_ip(vip):
    #r = requests.get('%snet_nat?zhuangtai=online&vip=%s&q_columns=["vip", "source_address_nat"]'% (url, vip), headers=headers)
    # r = requests.get('%snet_nat?vip=%s&q_columns=["vip", "source_address_nat"]'% (url, vip), headers=headers)
    # if r.status_code != 200:
    #     print 'ERROR: vip %s no SNAT IP!!!'
    #     return ''
    # result = r.json()['data']
    result = NET_NAT_VIP_DICT.get(vip)
    if not result:
        print 'ERROR: vip %s no SNAT IP!!!'
        return ''
    source_address_nat = []
    for re in result:
        source_address_nat.append(re['source_address_nat'])

    return list(set(source_address_nat))

def dns_vip(idc,vip):
    if idc == 'BX' and vip.startswith('30.6'):
        return True
    elif idc == 'WGQ' and vip.startswith('30.9'):
        return True
    else:
        return False

def get_vip_snat_batch(snat, dest_idc, total_snat_list):
    # r = requests.get('%snet_nat?source_address_nat=%s&q_columns=["vip", "source_address_nat"]'% (url, snat), headers=headers)
    # result = r.json()['data']

    result = NET_NAT_ADDRESS_NAT_DICT.get(snat, [])
    vip = []
    #source_address_nat_list = []
    for re in result:
        vip_tmp = re['vip']
        if dns_vip(dest_idc, vip_tmp):
            #change ip into not dest idc
            if vip_tmp.startswith('30.65'):
                vip_tmp = '30.97.' + vip_tmp.split('.')[2] + '.' + vip_tmp.split('.')[3]
            elif vip_tmp.startswith('30.97'):
                vip_tmp = '30.65.' + vip_tmp.split('.')[2] + '.' + vip_tmp.split('.')[3]
            print 'vip change into %s' % vip_tmp
        if re['source_address_nat'] not in total_snat_list:
            vip.append((vip_tmp, re['source_address_nat']))
            total_snat_list.append(re['source_address_nat'])
    vip=list(set(vip))
    return vip


def get_idc(ip):
    if ip.startswith('30.6'):
        idc = 'BX'
        return idc
    elif ip.startswith('30.9') or ip.startswith('30.10'):
        idc = 'WGQ'
        return idc
    else:
        print 'ERROR: ip %s no proper idc found' % ip
        sys.exit(1)

def main(domain_arr, dest_idc):
    """TODO: Docstring for main.

    :arg1: TODO
    :returns: TODO

    """
    print '\n\nNew loop +++++++++++++++++++++++++++++\n'


    if domain_arr.find(',') == -1:
        domain_arr = [domain_arr]
    else:
        domain_arr = domain_arr.split(',')

    total_snat_list = []
    print domain_arr
    pair_arr = []
    for domain in domain_arr:
        print '#########domain: %s begin'%domain
        #import pdb
        #pdb.set_trace()
        if domain == 'DUMB' or domain=='':
            continue
        # for inbound this array will be ip
        if domain.split('.')[-1].isdigit():
            # IN BOUND
            snat_in_bound_ip = domain
            in_bound_vip_list = get_inbound_vip(snat_in_bound_ip, dest_idc)
            if in_bound_vip_list:
                for in_bound_vip in in_bound_vip_list:
                    pair_arr += [(in_bound_vip, snat_in_bound_ip)]
            else:
                print 'ERROR: in_bound_vip_list is NULL for ip: %s'%domain

        else:
            vip = get_dns_domain(domain, None)

            if vip == '':
                print 'vip is NULL and this will stop'
                continue
            else:
                print 'vip is %s'%vip
                source_address_nat_list = get_snat_ip(vip)
                if source_address_nat_list == []:
                    print 'source_address_nat_list is NULL and this will stop'
                    continue
                else:
                    print 'source_address_nat_list is %s'%source_address_nat_list
                    #idc = get_idc(vip)
                    for source_address_nat in source_address_nat_list:
                        pair_arr_tmp = get_vip_snat_batch(source_address_nat, dest_idc, total_snat_list)
                        if pair_arr_tmp== []:
                            print 'domain: %s pair_arr_tmp is NULL and this will stop'%domain
                            continue
                        else:
                            pair_arr += pair_arr_tmp
                            print 'pair_arr_tmp are %s'%pair_arr_tmp
                            print 'type of pair_arr_tmp are %s'%type(pair_arr_tmp[0])
    pair_arr=list(set(pair_arr))
    pair_forcheck = pair_arr
    print "start gateway"
    import datetime
    print datetime.datetime.now()
    # while len(pair_arr) > batch:
    #     result=biggateway_network_switch(pair_arr[:batch])
    #     pair_arr = pair_arr[batch:]
    # result=biggateway_network_switch(pair_arr)
    result = run_loop(pair_arr)
    import datetime
    print "end gateway"
    print datetime.datetime.now()
    #try:
    #    res = checkRoute(pair_forcheck)
    #    print res
    #except:
    #    print "script problem"
    return 0


def swicth_biggateway_network(param):
    result = biggateway_network_switch(param)
    print "result is " + str(result)
    return result



def run_loop(pair_arr):
    results = {}
    thread_list = []

    pool = ThreadPoolExecutor(max_workers=16)
    batch = 50
    while len(pair_arr) > batch:
        future = pool.submit(swicth_biggateway_network, pair_arr[:batch])
        pair_arr = pair_arr[batch:]
        thread_list.append(future)
    future = pool.submit(swicth_biggateway_network, pair_arr)
    thread_list.append(future)
    for future in as_completed(thread_list):
        print future.result()

    pool.shutdown()

    return results


if __name__ == "__main__":
    domain_arr = sys.argv[1]
    inbound_snat_src_ip_arr = sys.argv[2]
    dest_idc = sys.argv[3]
    lock = threading.Lock()

    # init data DNS_INFO_DICT VS_DICT NET_NAT_VIP_DICT NET_NAT_ADDRESS_NAT_DICT
    dns_r = requests.get('%sdns_info?q_columns=["domain", "ip", "idc"]' % url, headers=headers)
    dns_result = dns_r.json()['data']
    for dns_info in dns_result:
        DNS_INFO_DICT.setdefault(dns_info['domain'], []).append(dns_info)

    vs_r = requests.get('%svs?q_columns=["name", "vip"]' % url, headers=headers)
    vs_result = vs_r.json()['data']
    for vs_info in vs_result:
        VS_DICT.setdefault(vs_info['vip'], []).append(vs_info)

    net_nat_r = requests.get('%snet_nat?q_columns=["vip", "source_address_nat"]' % url, headers=headers)
    net_nat_result = net_nat_r.json()['data']
    for net_nat_info in net_nat_result:
        NET_NAT_VIP_DICT.setdefault(net_nat_info['vip'], []).append(net_nat_info)
        NET_NAT_ADDRESS_NAT_DICT.setdefault(net_nat_info['source_address_nat'], []).append(net_nat_info)

    ret = main(domain_arr + ',' + inbound_snat_src_ip_arr, dest_idc)
    sys.exit(ret)
