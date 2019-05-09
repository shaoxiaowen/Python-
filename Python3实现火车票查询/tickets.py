"""命令行火车票查看器

Usage:
    tickets [-dgktz] <from> <to> <date>

Options:
    -h, --help 查看帮助
    -d         动车
    -g         高铁
    -k         快速
    -t         特快
    -z         直达

Examples:
    tickets 上海 北京 2016-10-10
    tickets -dg 成都 南京 2016-10-10
"""


import urllib.request
import ssl
import requests
import re
from docopt import docopt
from pprint import pprint
from stations import stations
from prettytable import PrettyTable
from colorama import init, Fore


init()


class TrainsData:
    header='车次 车站 时间 历时 商务座 一等 二等 高级软卧 软卧 硬卧 硬座 无座'.split()

    def __init__(self, available_trains, available_place, options):
        """
        available_trains:全部车次信息
        available_place:车站信息
        options:火车类型
        """
        self.available_trains = available_trains
        self.available_place = available_place
        self.options = options
    @property
    def trains(self):
        # Z281 |20190509|3|C1|08|17|0|0   ||高级软卧||软卧|||无座||硬卧|硬座|二等座|一等座|商务座||10401030|1413|0|0|null
        for raw_train in self.available_trains:
            raw_train_list = raw_train.split('|')
            train_no = raw_train_list[3]  # 车次
            initial = train_no[0].lower()  # 车次首字母
            # 如果没有
            if not self.options or initial in self.options:
                from_station = self.available_place[raw_train_list[6]]  # 出发站
                to_station = self.available_place[raw_train_list[7]]  # 到达站
                start_time = raw_train_list[8]  # 出发时间
                end_time = raw_train_list[9]  # 到达时间
                duration = raw_train_list[10]  # 历时
                swz = raw_train_list[-7]  # 商务座
                ydz = raw_train_list[-8]  # 一等座
                edz = raw_train_list[-9]  # 二等座
                gjrw = raw_train_list[-18]  # 高级软卧
                rw = raw_train_list[-16]  # 软卧
                yw = raw_train_list[-11]  # 硬卧
                yz = raw_train_list[-10]  # 硬座
                wz = raw_train_list[-13]  # 无座

                train = [
                    train_no,
                    '\n'.join([Fore.GREEN+from_station+Fore.RESET,
                               Fore.RED+to_station+Fore.RESET]),
                    '\n'.join([Fore.GREEN+start_time+Fore.RESET,
                               Fore.RED+end_time+Fore.RESET]),
                    duration,
                    swz if swz else '--',
                    ydz if ydz else '--',
                    edz if edz else '--',
                    gjrw if gjrw else '--',
                    rw if rw else '--',
                    yw if yw else '--',
                    yz if yz else '--',
                    wz if wz else '--'
                ]
                yield train
    def pretty_print(self):
        pt=PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)

# 解析命令行
def cli():
    """command-line interface"""
    # docopt 会根据我们在 docstring 中的定义的格式自动解析出参数并返回一个字典，也就是 arguments
    arguments = docopt(__doc__)
    """
    {'-d': True,
    '-g': True,
    '-k': False,
    '-t': False,
    '-z': False,
    '<date>': '2019-05-10',
    '<from>': '成都',
    '<to>': '南京'}
    """
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
    # ADULT 表示成人票
    url = f"https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={date}&leftTicketDTO.from_station={from_station}&leftTicketDTO.to_station={to_station}&purpose_codes=ADULT"
    # req=requests.get(url,verify=False)
    req = requests.get(url)
    # 使用 requests 提供的 r.json() 可以将 JSON 数据转化为 Python 字典
    available_trains = req.json()['data']['result']
    available_place = req.json()['data']['map']
    # 获取命令行中的选项
    options = ''.join(
        [key for key, value in arguments.items() if value is True])

    trainData = TrainsData(available_trains, available_place, options)
    trainData.pretty_print()

# 获取车站名称及对应代码，并存入stations.py中


def getStations():
    # 车站代码查询连接
    # https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9077
    url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8971"

    # 两种获取请求的响应数据的方式 urllib.request 或者 requests

    # 方式一  urllib.request
    # context=ssl._create_unverified_context()
    # result=urllib.request.urlopen(url,context=context).read().decode('utf-8')

    # 方式二  requests
    response = requests.get(url, verify=False)

    # 将车站数据转为字典有两种方式 一 正则表达式 二慢慢截取
    sdict = {}

    # 正则表达式
    stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text)
    sdict = dict(stations)

    pprint(sdict, indent=4)
    with open('stations.py', 'w', encoding='utf-8') as f:
        f.write("stations="+str(sdict))

    # 截取的方式
    # result = response.text.replace('var station_names =\'', '').replace(
    #     '\'', '').replace(';', '')
    # stations = result.strip().split('@')
    # for s in stations:
    #     if s is not "":
    #         sdict.update({s.split('|')[1]:s.split('|')[2]})

    return sdict


if __name__ == "__main__":
    # getStations() #先执行，获取车站数据，创建stations.py
    # print(stations)
    cli()
