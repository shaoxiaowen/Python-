import zipfile
import argparse
import os
from os.path import *

def tryZipwd(zipFile,password,savePath):
    try:
        zipFile.extractall(path=savePath,pwd=password.encode('utf-8'))
        print('[+] Zip File decompression success,password: %s'%password)
        return True
    except:
        print('[-] Zip File decompression failed,password: %s'%password)
def main():
    # 这里用描述创建了ArgumentParser对象
    parser=argparse.ArgumentParser(description='Brute Crack Zip')
    # 添加一行-H命令dest可以理解为解析是获取-H参数后面值的变量名，help是这里命令的帮助信息
    parser.add_argument('-f',dest='zFile',type=str,help='The zip file path.')
    parser.add_argument('-w',dest='pwdFile',type=str,help='Password dictionary file.')
    zFilePath=None
    pwdFilePath=None
    try:
        options=parser.parse_args()
        zFilePath=options.zFile
        pwdFilePath=options.pwdFile
    except:
        print(parser.parse_args(['-h']))
        exit(0)
    if zFilePath==None or pwdFilePath ==None:
        print(parser.parse_args(['-h']))
        exit(0)

    zFile=zipfile.ZipFile(zFilePath)
    f=open(pwdFilePath)

    for pwd in f.readlines():
        p,f=split(zFilePath) # os.path.split
        print(f"p:{p},f:{f}")
        dirName=f.split('.')[0]# 获取文件名
        dirPath=join(p,dirName) # os.path.join
        try:
            os.mkdir(dirPath)
        except:
            pass
        ok=tryZipwd(zFile,pwd.strip('\n'),dirPath)
        if ok:
            break
if __name__ == '__main__':
    main()
