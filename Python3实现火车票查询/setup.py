from setuptools import setup

setup(
    name='tickets',
    py_modules=['tickets','stations'],
    install_requires=['requests','docopt','prettytable','colorama'],
    entry_points={
        'console_scripts':['tickets=tickets:cli']
    }
)
# 执行 python3 setup.py install 安装
# tickets 北京 上海 2019-05-10 查询
# 通过 pip uninstall tickets 卸载
