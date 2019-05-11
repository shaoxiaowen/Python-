import sys
import os
import subprocess

from http.server import BaseHTTPRequestHandler, HTTPServer


class ServerException(Exception):
    '''服务器内部错误'''
    pass

# test方法用来判断是否符合该类指定的条件，act则是符合条件时的处理函数。
# 其中的handler是对RequestHandler实例的引用，通过它，我们就能调用handle_file进行响应。

class case_no_file(object):
    '''该路径不存在'''

    # 路径不存在 返回true，不存在返回false
    def test(self, handler):
        return not os.path.exists(handler.full_path)
    # 路径不存在 则抛出异常

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_existing_file(object):
    '''该路径是文件'''

    # 如果是文件 则返回true，不是文件 则返回false
    def test(self, handler):
        return os.path.isfile(handler.full_path)
    # 处理文件

    def act(self, handler):
        handler.handle_file(handler.full_path)


class case_always_fail(object):
    '''所有情况都不符合时的默认处理类'''

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

# 返回index.html
class case_directory_index_file(object):
    # 获取index.html的全路径
    def index_path(self,handler):
        return os.path.join(handler.full_path,'index.html')
    # 判断目标路径是否是目录&&目录下是否有index.html
    def test(self,handler):
        return os.path.isdir(handler.full_path) and \
            os.path.isfile(self.index_path(handler))
    # 响应index.html的内容
    def act(self,handler):
        handler.handle_file(self.index_path(handler))

class case_cgi_file(object):
    '''脚本文件处理'''
    def test(self,handler):
        return os.path.isfile(handler.full_path) and \
            handler.full_path.endswith('.py')
    def act(self,handler):
        #运行脚本文件
        handler.run_cgi(handler.full_path)
class RequestHandler(BaseHTTPRequestHandler):
    '''处理请求并返回页面'''

    # 页面模板
    Page = '''\
    <html>
    <body>
    <table>
    <tr>  <td>Header</td>         <td>Value</td>          </tr>
    <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
    <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
    <tr>  <td>Client port</td>    <td>{client_port}</td> </tr>
    <tr>  <td>Command</td>        <td>{command}</td>      </tr>
    <tr>  <td>Path</td>           <td>{path}</td>         </tr>
    </table>
    </body>
    </html>'''

    Error_Page = '''\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>'''

    Cases = [case_no_file(),
             case_cgi_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    # 处理一个GET请求，必须要实现的方法，用来接受http的get请求
    def do_GET(self):
        # page = self.create_page()
        # self.send_content(page)
        try:
            # 文件完整路径
            # os.getcwd() 是当前的工作目录
            # self.path 保存了请求的相对路径
            self.full_path = os.getcwd()+self.path

            # 遍历所有可能的情况
            for case in self.Cases:
                # 如果满足该类情况
                if case.test(self):
                    #调用响应的act函数
                    case.act(self)
                    break
        # 处理异常
        except Exception as msg:
            self.handle_error(msg)

    # def create_page(self):
    #     values = {
    #         'date_time'  :  self.date_time_string(),
    #         'client_host':  self.client_address[0],
    #         'client_port':  self.client_address[1],
    #         'command'    :  self.command,
    #         'path'       :  self.path
    #     }
    #     page=self.Page.format(**values)
    #     return page

    def send_content(self, page):
        self.send_response(200)
        self.send_header("Content_Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers
        # self.wfile.write(page.encode('utf-8'))
        self.wfile.write(page)

    def handle_file(self, full_path):
        try:
            # 以二进制的方式打开文件
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read:{1}".format(self.path, msg)
            self.handle_error(msg)

    # 处理出现错误的情况
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode('utf-8'))
    
    def run_cgi(self,full_path):
        data=subprocess.check_output(["python3",full_path],shell=False)
        self.send_content(data)


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
