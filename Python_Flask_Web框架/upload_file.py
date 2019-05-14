import os
from flask import Flask,request
from werkzeug.utils import secure_filename

UPLOAD_FOLDER='/Users/shaoxiaowen/Desktop/PythonCode/实验楼/Python_Flask_Web框架'
ALLOWED_EXTENSIONS=set(['txt','pdf','png','jpg','jpeg','gif'])

app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

def allowed_file(filename): #验证上传的文件名是否符合要求，文件名必须带点并且符合允许上传的文件类型
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS  #rsplit()从右向左寻找

@app.route('/',methods=['GET','POST'])
def upload_file():
    if request.method=='POST': #如果是POST请求方式
        uploadfile=request.files['file'] #获取上传的文件
        if uploadfile and allowed_file(uploadfile.filename): #如果文件存在并且符合要求
            uploadfile.save(os.path.join(app.config['UPLOAD_FOLDER'],uploadfile.filename))
            return '{} upload successed'.format(uploadfile.filename) #返回保存成功的信息
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''