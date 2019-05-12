from PIL import Image
import argparse

# 首先，构建命令行输入参数处理 ArgumentParser 实例
parser=argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('-o','--output') #输出文件
parser.add_argument('--width',type=int,default=80)#输出字符画宽度
parser.add_argument('--height',type=int,default=80)#输出字符画高度

# 解析并获取参数
args=parser.parse_args()

# 输入的图片文件的路径
IMG=args.file

# 输出字符画的宽度
WIDTH=args.width

# 输出字符画的高度
HEIGHT=args.height

# 输出字符画的路径
OUTPUT=args.output

# 字符画所使用的字符集，一共70个
ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
#实现RGB值转字符的函数
def get_char(r,g,b,alpha=256):
    """首先将RGB值转为灰度值，然后使用灰度值映射到字符列表的某个字符"""
    #判断 alpha的值，如果为0，表示图片中该位置为空白
    if alpha==0:
        return ' '
    
    # 获取字符集的长度，这里为70
    length=len(ascii_char)

    # 将RGB值转为灰度值 gray 灰度值范围:0-255
    gray=int(0.2126*r+0.7152*g+0.0722*b)

    # 灰度值范围是0-255 而字符集只有70
    #需要进行如下处理才能将灰度值映射到指定的字符上
    unit=(256.0+1)/length

    # 返回灰度值对应的字符
    return ascii_char[int(gray/unit)]

#表示如果 ascii.py 被当作 python 模块 import 的时候，这部分代码不会被执行
if __name__ == "__main__":
    # 使用PIL的Image.open打开图片文件，获得对象im
    im=Image.open(IMG)
    # 使用PIL库的im.resize()跳转图片大小对应的输出的字符画的高度和宽度
    # 注意第二个参数使用Image.NEAREST,表示输出低质量的图片。
    im=im.resize((WIDTH,HEIGHT),Image.NEAREST)

    #初始化输出的字符串
    txt=""
    

    # 遍历提取图片中每行的像素的RGB值，调用getchar转为对应的字符
    for i in range(HEIGHT):
        for j in range(WIDTH):
            # 将（j,i）坐标的RGB像素转为字符后添加到txt字符串
            # 获取得到坐标 (j,i) 位置的 RGB 像素值（有的时候会包含 alpha 值），
            # 返回的结果是一个元组，例如 (1,2,3) 或者 (1,2,3,0)。
            # 我们使用 * 可以将元组作为参数传递给 get_char，
            # 同时元组中的每个元素都对应到 get_char 函数的每个参数
            txt+=get_char(*im.getpixel((j,i)))
        # 遍历完一行后需要增加换行符
        txt+='\n'
    print(txt)

    # 字符画输出到文件
    if OUTPUT:
        with open(OUTPUT,'w') as f:
            f.write(txt)
    else:
        with open("output.txt",'w') as f:
            f.write(txt)
