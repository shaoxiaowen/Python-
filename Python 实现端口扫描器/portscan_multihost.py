from socket import *
import threading
import sys

lock=threading.RLock()


def tcp_test(port):
    sock=socket()
    sock.settimeout(10)
    result=sock.connect_ex((target_ip,port))
    if result == 0:
        lock.acquire()
        print("opened ports:{}",port)
        lock.release()
    


if __name__=='__main__':
    # multi_scan.py <host> <start>-<end port>
    
    hosts = []
    ports = []
    with open("allhost.md") as f:
        hosts.append(f.readline())
    
    with open("allhost.md") as f:
        ports.append(f.readline())

    for host in hosts:
        target_ip=gethostbyname(host)

        for port in ports:
            port =int(port)
            t=threading.Thread(target=tcp_test,args=(port,))
            t.start()