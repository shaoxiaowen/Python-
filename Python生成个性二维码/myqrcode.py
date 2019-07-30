# -*- coding: utf-8 -*-
'''
# Created on 七月-30-19 22:29
# myqrcode.py
# @author: shaoxiaowen
# @description: myqr可以将网页，文字 都转为二维码
'''
from MyQR import myqr
import argparse

# words="https://blog.csdn.net/fighting_sxw",
# 普通二维码
def generate_normal_qrcode(words):
    myqr.run(
        words=words,
        save_name='myQrCode.png'
    )

#

# 带图片的艺术二维码：黑白

# picture='1_fighting_sxw.jpg',
def generate_blackAndWhite_qrcode(words,picture):
    myqr.run(
        words=words,
        picture=picture,
        save_name="myQrCode.png"
    )

# 带图片的艺术二维码：彩色


def generate_color_qrcode(words,picture):
    myqr.run(
        words=words,
        picture=picture,
        colorized=True,
        save_name="myQrCode.png"
    )

# 动态二维码

# picture='新垣结衣.gif'
def generate_gif_qrcode(words,picture):
    myqr.run(
        words=words,
        picture=picture,
        colorized=True,
        save_name="myQrCode.gif"
    )



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = "Python生成个性二维码工具"
    parser.add_argument('-n',"--normal", help="普通二维码",action="store_true")
    parser.add_argument('-baw',"--blackAndWhite", help="黑白二维码",action="store_true")
    parser.add_argument('-c',"--color", help="彩色二维码",action="store_true")
    parser.add_argument('-g',"--gif", help="动态二维码",action="store_true")
    parser.add_argument('-w','--words',help="需要转换的内容")
    parser.add_argument('-p','--picture',help="背景图片地址")

    args = parser.parse_args()
    if args.normal:
        print("普通二维码")
        generate_normal_qrcode(args.words)
    elif args.blackAndWhite:
        print("黑白二维码")
        generate_blackAndWhite_qrcode(args.words,args.picture)
    elif args.color:
        print("彩色二维码")
        generate_color_qrcode(args.words,args.picture)
    elif args.gif:
        print("动态二维码")
        generate_gif_qrcode(args.words,args.picture)

