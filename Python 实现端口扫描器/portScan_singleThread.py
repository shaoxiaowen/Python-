#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
from socket import *


# postscan.py <host> <start_port>-<end>

host = sys.argv[1]
ports = sys.argv[2].split('-')

start_port = int(ports[0])
end_port = int(ports[1])

target_ip = gethostbyname(host)

opened_ports=[]
print(f"端口范围:{start_port}-{end_port}")

print(f"主机ip:{target_ip}")

for port in range(start_port,end_port+1):

    print(f"正在扫描端口：{port}")
    sock=socket() #默认参数就可以，所以不用写参数
    sock.settimeout(10)
    result = sock.connect_ex((target_ip,port))
    print(f"result:{result}")
    if result ==0:
        opened_ports.append(port)
        print("开放端口：{port}")

print("oppened ports:")

for i in opened_ports:
    print(i)