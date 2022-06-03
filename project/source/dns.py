import string
import requests
from flask import Flask, make_response
import time
import sys

app = Flask(__name__)

pre_port = 0
port_list = []

class Dns:
    # fixme: 这里要读取文件找到端口
    @staticmethod
    @app.route('/dnsRequest')
    def makeDnsRerurn():
        global pre_port
        # choose file according to the input filename
        pre_port = (pre_port + 1) % len(port_list)

        return make_response(str(port_list[pre_port]))


if __name__ == '__main__':
    file_name = sys.argv[1]
    with open(file_name, 'r') as f:
        for line in f.readlines():
            port_list.append(line.strip())
    
    app.run(host="localhost",port=7775)