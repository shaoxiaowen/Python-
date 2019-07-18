from MyQR import myqr

# myqr可以将网页，文字 都转为二维码

# 普通二维码

# myqr.run(
#     words="https://blog.csdn.net/fighting_sxw",
#     save_name='myblog.png'
#     )

#

# 带图片的艺术二维码：黑白
# myqr.run(
#     words="https://blog.csdn.net/fighting_sxw",
#     picture='1_fighting_sxw.jpg',
#     save_name="myblog1.png"
# )

# 带图片的艺术二维码：彩色
# myqr.run(
#     words="https://blog.csdn.net/fighting_sxw",
#     picture='1_fighting_sxw.jpg',
#     colorized=True,
#     save_name="myblog2.png"
# )

#动态二维码

myqr.run(
    words="https://blog.csdn.net/fighting_sxw",
    picture='新垣结衣.gif',
    colorized=True,
    save_name="myblog3.gif"
)

#将文字生成二维码

myqr.run(
    words="hello python",
    colorized=True,
    save_name="text.png"
)

