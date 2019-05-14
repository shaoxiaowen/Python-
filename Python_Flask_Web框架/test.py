from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

# 设置密钥，保证会话安全
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():
    print("主页")
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/logout')
def logout():
    # 如果用户名存在，则会从会话中移除该用户
    session.pop('username', None)
    return redirect(url_for('index'))
