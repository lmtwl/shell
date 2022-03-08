#!/usr/bin/python
# _*_coding:utf-8_*_
# Author: Tian Fuyuan
#python3 bgpconfig.py -c allhk -m 10

import os 
import argparse
import threading
import math


AS_CMD='vtysh -c "show run" | grep "router bgp"'
BGP_CIDR_LIST_CMD='vtysh -c "show run" | grep network | grep -v area | grep -v import'

def load_ip_from_file(ip_file_path):
    if not os.path.exists(ip_file_path):
        raise FileNotFoundError(f'指定的文件{ip_file_path}不存在！')
    with open(ip_file_path, 'r') as f:
        return f.read().splitlines()

def get_as_number():
    return os.popen(AS_CMD).read().strip().split()[-1]

def get_bgp_cidr_list():
    r = []
    bgp_list = os.popen(BGP_CIDR_LIST_CMD).read().splitlines()
    for line in bgp_list:
        r.append(line.split()[-1])
    return r

def add_ip(iplist, local_as): 
    for ip in iplist:
        if ip.startswith('10.'):
            continue 
        print(f'增加{ip}')
        add_cmd = f'vtysh -c "configure t " -c "router bgp {local_as}" -c "network {ip}"'
        os.popen(add_cmd)

def del_ip(iplist, local_as):
    for ip in iplist:
        if ip.startswith('10.'):
            continue 
        print(f'删除{ip}')
        del_cmd = f'vtysh -c "configure t" -c "router bgp {local_as}" -c "no network {ip}"'
        os.popen(del_cmd)

def split_list(origin_list, num):
    length = len(origin_list)
    if num <= 0 or num > length:
        return [origin_list]
    n = int(math.ceil(length / float(num)))
    return [origin_list[i:i + n] for i in range(0, len(origin_list), n)]


def exec_in_multi(lists, target, local_as):
    thread_list = []
    for list in lists:
        t = threading.Thread(target=target, args=(list, local_as))
        t.setDaemon(True)
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()

def action(ip_file_path, thread_num):
    local_as = get_as_number()
    bgpip_list = get_bgp_cidr_list()
    fileip_list = load_ip_from_file(ip_file_path)
    ip_to_add = list(set(fileip_list) - set(bgpip_list))
    ip_to_del = list(set(bgpip_list) - set(fileip_list))
    splited_add_ip = split_list(ip_to_add, thread_num)
    splited_del_ip = split_list(ip_to_del, thread_num)
    exec_in_multi(splited_add_ip, add_ip, local_as)
    exec_in_multi(splited_del_ip, del_ip, local_as)
    print('脚本运行完毕')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('-m', '--multi' , type=int)
    args = parser.parse_args()
    action(args.config, args.multi)

