import paramiko
import time
import sys
from get_pwd import s

user = "root"
add = "3.3.3.3"
#passwd = s("AutoOP","BX_CiscoRouterSSH",user,add)
#hosts = ["30.159.0.30","30.159.0.31","30.95.0.33","30.95.0.34","30.127.0.33","30.127.0.34"]

def setlistenerrule(ip, rule):
    cmd = "tmsh modify gtm listener all rules { %s }"%rule
    print cmd
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip,username=user,password=passwd,timeout=10,allow_agent=False,look_for_keys=False)
    except:
        print "can connect to gtm!"
        return
    chan = ssh.invoke_shell()
    chan.settimeout(10)
    chan.send(cmd+"\n")
    print chan.recv(9999)
    time.sleep(2)
    chan.close()
    ssh.close()

def setlistenerrule_new(ip, rule, user, passwd):
    cmd = "tmsh modify gtm listener all rules { %s }"%rule
    print cmd
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip,username=user,password=passwd,timeout=10,allow_agent=False,look_for_keys=False)
    except:
        print "can connect to gtm!"
        return
    chan = ssh.invoke_shell()
    chan.settimeout(10)
    chan.send(cmd+"\n")
    print chan.recv(9999)
    time.sleep(2)
    chan.close()
    ssh.close()



def ipv6_on():
    print('ipv6 on!!!')
    rule = "irule_ipv6_whitelist_allow_domain"
    user = "root"
    add = "3.3.3.3"
    #passwd = s("AutoOP","BX_CiscoRouterSSH",user,add)
    hosts = ["30.95.0.33","30.95.0.34","30.127.0.33","30.127.0.34"]
    for h in hosts:
        setlistenerrule_new(h,rule, user, "Ro@1hblsqt")


def ipv6_off():
    print('ipv6 off!!!')
    rule = "ipv6_no_error"
    user = "root"
    add = "3.3.3.3"
    #passwd = s("AutoOP","BX_CiscoRouterSSH",user,add)
    hosts = ["30.95.0.33","30.95.0.34","30.127.0.33","30.127.0.34"]
    for h in hosts:
        setlistenerrule_new(h,rule, user, "Ro@1hblsqt")
    


if __name__ == "__main__":
    hosts = ["30.95.0.33","30.95.0.34","30.127.0.33","30.127.0.34"]
    p = sys.argv[1]
    rule = "ipv6_no_error" if p=="off" else "irule_ipv6_whitelist_allow_domain" if p=="on" else None

    assert rule is not None
    #print rule

    for h in hosts:
        setlistenerrule(h,rule)

