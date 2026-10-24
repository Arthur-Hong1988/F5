#!/usr/bin/env python
# usage: running in Control node
from __future__ import division
import os
import sys
import subprocess
import logging
import json

#logging.basicConfig(level=logging.DEBUG,
#	format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#	datefmt='%a, %d %b %Y %H:%M:%S',
#	filename='/var/log/get_lucloud_usage.log',
#	filemode='w')

#def shell_source(script):
#    """Sometime you want to emulate the action of "source" in bash,
#    settings some environment variables. Here is a way to do it."""
#    pipe = subprocess.Popen(". %s; env" % script, stdout=subprocess.PIPE, shell=True)
#    output = pipe.communicate()[0]
#    env = dict((line.split("=", 1) for line in output.splitlines()))
#    os.environ.update(env)

def exe_cmd(cur_cmd, **kwargs):
    """TODO: Docstring for function.
    :returns: TODO

    """
    if kwargs.get('shell') is True:
        output = subprocess.check_output(cur_cmd, universal_newlines=True, **kwargs).split('\n')
    else:
        output = subprocess.check_output(cur_cmd.split(), universal_newlines=True, **kwargs).split('\n')
    #print 'output is %s'%output
    return output


if __name__ == "__main__":
    #SET DEPLOY_WEIGHT = y
    #SET PLAN_ID = 748
    #SET DEPLOY_VS_IP_PORT = 1.1.1.3:80
    #SET TASK_ID = 683
    #SET DEPLOY_VS_IP = 1.1.1.3
    #SET APP = test-task-f5-q
    #SET DEPLOY_POOL_MEMBERS = ["172.23.44.127:8000"]
    #SET DEPLOY_POOL_NAME = pavo_dev_master
    #SET DEPLOY_VS_NAME = dev_master
    #SET DEPLOY_OBJECT = vs
    #SET DEPLOY_F5_IP = 172.168.86.251
    #SET DEPLOY_TYPE = add_pool_vs

    print '\n\n+++++++++++++++++++NEW Loop+++++++++++++++++++++++++++++\n'
    # args like {"f5_ip":"172.168.86.251", "task_id":"123", "op_params":{"pool1":{"name":}}}
    # export DEPLOY_OBJECT='{"pool_name": "pool_pavo_new_0502_2", "snat_pool_members": "3.3.7.1", "area": "DEV", "area_domain": "DEV", "vip": "1.1.1.101", "pool_description": "", "f5_ip": "172.168.86.251",     "vs_name": "vs_pavo_new_0502_2", "vs_description": "", "pool_loadBalancingMode": "", "translatePort": "enabled", "vs_ip_port": "1.1.1.101:80", "vs_profiles": "{"kind": "ltm:virtual:profile", "name": "fastL4    _tw_rewrite"}", "vs_ipProtocol": "", "snat_pool_name": "snat_pool_name_test", "pool_monitor": "", "pool_members": "2.2.2.1:8000"}'
    # /wls/applications/exec_change.py  \'{"f5_ip":"%s", "task_id":"%s", "deploy_object": "%s" "op_params":{"snat1":{"name":"%s", "members":"%s"}, "pool1":{"name":"%s", "members":"%s"}, "vs1":{"name":"%s", "destination":"%s", "pool":"%s"}}}\' >> /wls/logs/f5_add_change.log' % (f5_ip, task_id, deploy_object, deploy_object['snat_pool_name'], deploy_object['snat_pool_members'], pool_name, pool_members, vs_name,vs_ip_port, pool_name)

    #print sys.argv[1]
    params = json.loads(sys.argv[1])
    task_id = params['task_id']
    f5_ip = params['f5_ip']
    deploy_object = params['deploy_object']
    #deploy_object = params['deploy_object']
    op_params = params['op_params']
    suffix = exe_cmd('date +%Y_%m_%d_%H:%M:%S', shell=True)[0]
    new_file_path = '/wls/applications/change_history/1.f5.cfg_' + task_id + '_' + suffix
    print 'new_file_path... is %s'%new_file_path

    # keeep section order 
    cmd = 'ls /tmp/;cp /wls/applications/1.f5.cfg ' + new_file_path   
    exe_cmd(cmd, shell=True)

    #print deploy_object
    # add extra fields into params 
    if deploy_object['snat_pool_name'] == '':
        op_params['vs1']['sourceAddressTranslation'] = {'type':'none'} 
    else:
        op_params['vs1']['sourceAddressTranslation'] = json.dumps({'type':'snat', 'pool':deploy_object['snat_pool_name']})
        op_params['snat_pool1'] = {}
        op_params['snat_pool1']['name'] = deploy_object['snat_pool_name']
        if 'snat_pool_members' in deploy_object.keys() and deploy_object['snat_pool_members'] != '':
            op_params['snat_pool1']['members'] = deploy_object['snat_pool_members']

        if 'snat_ip' in deploy_object.keys() and deploy_object['snat_ip'] != '':
            op_params['snat_pool1']['members'] = deploy_object['snat_ip']

        #other extra params
        if 'vs_description' in deploy_object.keys() and deploy_object['vs_description'] != '':
            op_params['vs1']['description'] = deploy_object['vs_description']
        op_params['vs1']['mask'] = '255.255.255.255'
        op_params['vs1']['pool'] = deploy_object['pool_name']

        if 'vs_ipProtocol' in deploy_object.keys() and deploy_object['vs_ipProtocol'] != '':
            op_params['vs1']['ipProtocol'] = deploy_object['vs_ipProtocol']
        #from ipdb import set_trace;set_trace()
        if 'vs_profiles' in deploy_object.keys() and deploy_object['vs_profiles'] != '' and deploy_object['vs_profiles'] != {}:
            op_params['vs1']['profiles'] = json.loads(deploy_object['vs_profiles'])


        if 'pool_loadBalancingMode' in deploy_object.keys() and deploy_object['pool_loadBalancingMode'] != '':
            op_params['pool1']['loadBalancingMode'] = deploy_object['pool_loadBalancingMode']

        if 'pool_monitor' in deploy_object.keys() and deploy_object['pool_monitor'] != '':
            op_params['pool1']['monitor'] = deploy_object['pool_monitor']

    #print op_params

    # process op_params
    cmd = ''
    for sec_key, sec_value in op_params.items():
        for sec_2key, sec_2value in sec_value.items():
            #print sec_2key
            #print sec_2value
            #cmd += 'crudini --set  ' + str(new_file_path) + ' ' + str(sec_key) + ' ' + str(sec_2key) + ' ' + str(sec_2value) +';'
            if sec_2key == 'profiles':
                cmd += "crudini --set  %s '%s' '%s' '%s';"%(new_file_path, sec_key, sec_2key, json.dumps(sec_2value)) 
            else:
                cmd += "crudini --set  %s '%s' '%s' '%s';"%(new_file_path, sec_key, sec_2key, sec_2value) 
            #print cmd
     
    exe_cmd(cmd, shell=True)

    # exec actual cmd
    #python2.7 /wls/applications/add_biggateway_file.py -t add -ip 172.168.86.251 -w n -f ./1.f5.cfg
    print("11111111")
    cmd = "python2.7 /wls/applications/add_biggateway_file.py -t add -ip %s -w n -f %s"%(f5_ip, new_file_path)
    print(cmd)
    cmd_output = exe_cmd(cmd, shell=True)
    print cmd_output
