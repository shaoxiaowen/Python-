#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import threading
from socket import *

lock=threading.RLock()

def tcp_test(port):
    sock = socket()
    sock.settimeout(10)
    result =sock.connect_ex((target_ip,port))
    if result == 0:
        #加锁
        lock.acquire()
        print("Opened Port:{}".format(port))
        lock.release()
if __name__=='__main__':
    host=sys.argv[1]
    portstrs=sys.argv[2].split('-')

    start_port=int(portstrs[0])
    end_port=int(portstrs[1])

    target_ip=gethostbyname(host)

    for port in range(start_port,end_port):
        t=threading.Thread(target=tcp_test,args=(port,))
        t.start()

