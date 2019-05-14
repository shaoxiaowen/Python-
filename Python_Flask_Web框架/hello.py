from flask import Flask
from flask import request
from flask import render_template
from flask import abort,redirect,url_for
app = Flask(__name__)

@app.route('/')
def index():
    print(url_for('login'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    print("请求中断")
    abort(401)
@app.errorhandler(401)
def page_not_found(error):
    return render_template('page_not_found.html'),404

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == "POST":
#         return "POST请求，username:{},password:{}".format(
#             # post请求的参数
#             request.form['username'],
#             request.form['password'])
#     else:
#         return "GET请求，username:{},password:{}".format(
#             # get请求的参数
#             request.args.get("username","空值"),
#             request.args.get("password","空值"))



@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):  # 默认name为None
    print(name)
    return render_template('hello.html', name=name)  # 将 name 参数传递到模板变量中

# 如果访问 /,返回Index Page
@app.route('/')
def hello_world():
    return 'Index Page'


@app.route('/user/<username>')
def show_user_profile(username):
    # 显示用户名
    return 'User {}'.format(username)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # 显示提交整型的用户“id”的结果，注意“int”是将输入的字符串形式转换为整型数据
    return 'Post {}'.format(post_id)


@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # 显示 /path/之后的路径名
    return 'Subpath {}'.format(subpath)


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/about')
def about():
    return 'The about page'

@app.route('/sum/<int:a>/<int:b>')
def get_sum(a, b):
    return '{0}+{1}={2}'.format(a, b, a+b)
