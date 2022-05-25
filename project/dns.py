import string
import requests
import socket
from flask import Flask, make_response
import time
import sys

app = Flask(__name__)

# 判断端口是否被占用
def is_open(port, host = 127.0.0.1) -> bool:
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, int(port)))
        return True
    except socket.error:
        return False
    finally:
        if s:
            s.close()




class Dns:
    # fixme: 这里要读取文件找到端口
    file_name = '' # 传入 servers/2servers 类似的参数
    pre_port = 0

    def __init__(self, file:str){
        self.file_name = file
        self.pre_port = 0
    }
    
    
    @staticmethod
    @app.route('/dnsRequest')
    def makeDnsRerurn():
        # choose file according to the input filename
        f = open(file_name, encoding = "utf-8")
        port_list = []
        for line in f.readlines():
            port_list.append(line.strip())
        
        cnt = 0
        for port in port_list:
            if not is_open(port): # 如果端口不开放，立即返回该未被占用的端口
                pre_port = cnt
                cnt = cnt + 1
                return make_response(port)
            else:
                cnt = cnt + 1
        
        # round robin
        return make_response(port_list[(pre_port + 1) % len(port_list)])


        
        # return make_response('8080')#  这个函数非常好用,请修改内容




if __name__ == '__main__':
    app.run(host="localhost",port=7777)