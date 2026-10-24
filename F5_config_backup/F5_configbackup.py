# Edit by Arthur 20201228
##############################################
# 1.F5设备清单位置/home/wls81/f5devicelist.txt
# 30.95.0.29 root Ro@1hb1sqt B-G09-INT-LTM-01
# 30.95.0.33 root Ro@1hb1sqt B-G09-INT-GTM-01
#
# 2.逐行获取清单中的设备IP，用户名、密码、设备名
#
# 3.备份文件存放位置/wls/networkdaily/20201228/
#
# 4.脚本有3个方法一个是backup，一个是scp，一个是delete
# 用于测试针对F5配置文件的备份，拷贝，删除操作的效果
###############################################

import time
import os
import pexpect
import shutil


def backup():
    child = pexpect.spawn('ssh %s@%s' % (username, network_ip), timeout=20)
    res = child.expect(["password:"])
    # 它最后会返回 0 表示匹配到了所需的关键字
    # 如果后面的匹配关键字是一个列表的话，就会返回一个数字表示匹配到了列表中第几个关键字，从0开始计算
    if res == 0:
        child.sendline(password)
        child.expect('#')
        child.sendline("tmsh")
        child.expect('#')
        child.sendline("save sys ucs %s-%s.ucs" % (hostname, date))
        child.expect('#')
        child.sendline("quit")
        child.expect('#')
        child.sendline("quit")


def scp():
    cmd = "/usr/bin/scp %s@%s:/var/local/ucs/%s-%s.ucs /wls/networkdaily/%s" % (username, network_ip, hostname, date, date)
    foo = pexpect.spawn(cmd)
    index = foo.expect(["password:"])
    if index == 0:
        foo.sendline(password)
        time.sleep(5)


def delete():
    child = pexpect.spawn('ssh %s@%s' % (username, network_ip), timeout=10)
    res = child.expect(["password:"])
    if res == 0:
        child.sendline(password)
        child.expect('#')
        child.sendline("cd /var/local/ucs")
        child.expect('#')
        child.sendline("rm -f %s-%s.ucs" % (hostname, date))
        child.expect('#')
        child.sendline("exit")


def main():
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    if os.path.exists("/wls/networkdaily/%s" % date):
        shutil.rmtree("/wls/networkdaily/%s" % date)
    os.makedirs("/wls/networkdaily/%s" % date)
    with open("/home/wls81/f5devicelist.txt") as hello_file:
        for line in hello_file:
            network_ip = line.split(' ')[0].strip()
            username = line.split(' ')[1].strip()
            password = line.split(' ')[2].strip()
            hostname = line.split(' ')[3].strip()
            global date
            global network_ip
            global username
            global password
            global hostname
            backup()
            scp()
            delete()


if __name__ == "__main__":
    main()
