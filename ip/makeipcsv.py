#!/usr/bin/env python
# _*_coding:utf-8_*_
import sys
import os
import csv
import socket
import struct
import netaddr
from netaddr import *
def cidrs(sip,eip,col):
    r = []
    cidr =netaddr.iprange_to_cidrs(sip, eip)
#   print(cidr)
    for k, v in enumerate(cidr):
        tmp = []
        tmp.append(str(v))
        tmp.extend(col)
        r.append(tmp)
    return r
csvFile=open("IP-COUNTRY-REGION-CITY.CSV","r")
reader = csv.reader(csvFile)
result = []
for line in reader:
    line[0]=socket.inet_ntoa(struct.pack('I',socket.htonl(int(line[0]))))
    line[1]=socket.inet_ntoa(struct.pack('I',socket.htonl(int(line[1]))))
    #print("----------------------------")
    #print(line[0],line[1],line[2])
    result.extend(cidrs(line[0],line[1],line[2:]))
with open('test_out.csv', 'w') as f:
    f_csv = csv.writer(f)
    f_csv.writerows(result)
