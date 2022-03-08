import os
import csv
import IPy
import re
import sys
from collections import deque


class MyDict(dict):

    def __missing__(self, key):
        value = self[key] = type(self)()
        return value
        
    @staticmethod
    def load(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f'指定的文件{path}不存在！')
        with open(path, 'r') as f:
            data = csv.reader(f)
            ip_dict = MyDict()
            ip_dict_reversed = MyDict()
            for i in data:
                arrs = re.split("[./]", i[0])
                ip_dict[arrs[0]][arrs[1]][arrs[2]][arrs[3]][arrs[4]] = True
                ip_dict_reversed[arrs[4]][arrs[0]][arrs[1]][arrs[2]][arrs[3]] = True
            return ip_dict, ip_dict_reversed


def get_from_cidr(ip_dict, cidr_address):
        arrs = re.split('[./]', cidr_address)
        try:
            result =  ip_dict.get(arrs[0]).get(arrs[1]).get(arrs[2]).get(arrs[3]).get(arrs[4])
            return result
        except Exception as e:
            return False

def get_from_prefix(ip_dict_reversed, local):
        result = []
        cidr_address = IPy.IP(local[0], make_net=True)
        prefix = cidr_address.prefixlen()
        full_match = int(prefix) // 8
        broadcast = str(cidr_address.broadcast()).split('.')
        arrs = re.split('[./]', str(cidr_address))
        full_search = arrs[:full_match]
        broadcast_search = full_match  if full_match  < 4 else 3
        broadcast_search_start = arrs[broadcast_search]
        broadcast_search_end = broadcast[broadcast_search]
        for key,value in ip_dict_reversed.items():
            #如果掩码比待比较的掩码大则跳过
            if int(key) < int(prefix):
                continue
            search_base = value
            search_result = []
            
            #如果全匹配的位没有全匹配跳过
            for search_key in full_search:
                search_base = search_base.get(search_key, {})
            if not search_base:
                continue

            #广播地址匹配的位匹配才能遍历
            for broadcast_search_key, broadcast_search_value in search_base.items():
                if int(broadcast_search_key) < int(broadcast_search_start) or int(broadcast_search_key) > int(broadcast_search_end):
                    continue
                search_result.extend(dfs_tree({broadcast_search_key: broadcast_search_value}))

            for ip in search_result:
                tmp = list(full_search)
                tmp.extend(ip)
                true_ip = '.'.join(tmp) + f'/{key}'
                tmp = list(local)
                tmp[0] = true_ip
                result.append(tmp)
        
        return result
 
def dfs_tree(root):
        node_stack = deque()
        path_stack = deque()
        result = []
        node_stack.appendleft(root)
        path_stack.appendleft([])
        while len(node_stack):
            current_node = node_stack.popleft()
            current_path = path_stack.popleft()
            if current_node == True:
                result.append(current_path)
            else:
                for key,value in current_node.items():
                    node_stack.appendleft(value)
                    tmp = list(current_path)
                    tmp.append(key)
                    path_stack.appendleft(tmp)
        return result
              

        

def filter_ip(local_path, ipip_path):
    result = []
    ipip_dict, ip_dict_reversed = MyDict.load(ipip_path)
    with open(local_path, 'r') as file:
        local_csv = csv.reader(file)
        for local in local_csv:
            print(','.join(local))
            r = get_from_cidr(ipip_dict, local[0])
            if r:
                result.append(local)
                continue
            extend_local = IPy.IP(local[0], make_net=True)
            found = False
            prefix_runout = False
            while not (prefix_runout or found):
                prefix = extend_local.prefixlen()
                prefix = int(prefix) -1
                extend_local = IPy.IP(str(extend_local).split('/')[0]).make_net(prefix)
                if prefix > 1 :
                    r = get_from_cidr(ipip_dict, str(extend_local))
                    if not r:
                        continue
                    result.append(local)
                    found = True
                else:
                    prefix_runout = True
            
            if not found:
                r = get_from_prefix(ip_dict_reversed, local)
                result += r
    print('查询完毕开始生成文件')
    with open('./result', 'w') as file:
        for r in result:
            line = ','.join(r)
            file.write(f'{line}\n')
    return result

if __name__ == '__main__':
    filter_ip(sys.argv[1], sys.argv[2])
                

            

            

            
    



            
            

   
#python  filter.py allruyd allru
