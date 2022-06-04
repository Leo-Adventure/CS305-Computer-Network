
import string
import requests
from flask import Flask, Response, request, make_response, send_file
import time
import sys
import xml.dom.minidom
 

app = Flask(__name__)



class ClientElement:
    def __init__(self, key) -> None:
        self.throughput = 0
        self.server_port = 0
        self.key = key
        self.bitrate_list = list()
        self.danmulist_topush = []
    
    def getURL(self) ->string:
        return "http://localhost:" + str(self.server_port)


class ClientSelf:
    headerSelf = {}
    log_path = ""
    alpha = 0.5
    dns_port = 7777
    dict_client = {}  #这个字典key是client的cookie的ID，key : ClientElement
    current_id = 0
    history_danmu = []
        


    @staticmethod
    @app.route('/index.html')
    def query_index():
        ClientSelf.dict_client.update({ClientSelf.current_id:ClientElement(ClientSelf.current_id)})
        current_client = ClientSelf.dict_client.get(ClientSelf.current_id)
        current_client.server_port = ClientSelf.request_dns()
        current_client.danmulist_topush = ClientSelf.history_danmu
        ClientSelf.headerSelf = {"Connection": "Keep-Alive", "Keep-Alive": "timeout=60, max=100"}  
        # request_temp = requests.get(current_client.getURL()+ "/index.html", headers=ClientSelf.headerSelf)
        html_file = "index4.html"

        to_return =send_file(html_file)
        to_return.set_cookie("ID",str(current_client.key), max_age=7200)

        ClientSelf.current_id = ClientSelf.current_id+1
        return to_return

    @staticmethod
    @app.route('/swfobject.js')
    def query_sw():
        cookie = request.cookies
        cur_client_id = int(cookie.get("ID"))
        current_client = ClientSelf.dict_client.get(cur_client_id)
        return Response(requests.get(current_client.getURL() + "/swfobject.js", headers=ClientSelf.headerSelf))

    @staticmethod
    @app.route('/StrobeMediaPlayback.swf')
    def query_strobe():
        cookie = request.cookies
        cur_client_id = int(cookie.get("ID"))
        current_client = ClientSelf.dict_client.get(cur_client_id)
        return Response(requests.get(current_client.getURL() + "/StrobeMediaPlayback.swf", headers=ClientSelf.headerSelf))


    @staticmethod
    @app.route('/vod/big_buck_bunny.f4m')
    def modify_request():
        """
            Here you should change the requested bit rate according to your computation of throughput.
            And if the request is for big_buck_bunny.f4m, you should instead request big_buck_bunny_nolist.f4m
            for client and leave big_buck_bunny.f4m for the use in proxy.
        """
        cookie = request.cookies
        cur_client_id = int(cookie.get("ID"))
        current_client = ClientSelf.dict_client.get(cur_client_id)
        print(current_client.getURL())
        response_for_proxy = requests.get(current_client.getURL() + "/vod/big_buck_bunny.f4m")
        # 问题出现不在上面一行,它这个提示错误是在最后一行
        # store the information into f4m file
        receive_file = "receive.f4m"
        with open(receive_file, "wb") as f:
            f.write(response_for_proxy.content)

        # analize the bitrate from f4m file and store it
        dom = xml.dom.minidom.parse(receive_file)
        root = dom.documentElement        
        media_list = root.getElementsByTagName("media")
        for media in media_list:
            current_client.bitrate_list.append(int(media.getAttribute("bitrate")))

        return Response(requests.get(current_client.getURL() + "/vod/big_buck_bunny_nolist.f4m"))


    @staticmethod
    @app.route('/vod/<int:rate>Seg<int:segment>-Frag<int:frag>')
    def forward_segment(rate, segment, frag):
        """
            Here you should change the requested bit rate according to your computation of throughput.
            And if the request is for big_buck_bunny.f4m, you should instead request big_buck_bunny_nolist.f4m
            for client and leave big_buck_bunny.f4m for the use in proxy.
        """
  
        cookie = request.cookies
        cur_client_id = int(cookie.get("ID"))     
        current_client = ClientSelf.dict_client.get(cur_client_id)
        print(current_client.getURL())
        # to select a proper bitrate
        bound_bitrate = current_client.throughput / 1.5
        # print(bound_bitrate)
        selected_bitrate = 10  # todo 这里不是很清楚，现在默认，如果bound_bitrate小于10，还是给10，这是最小的bit了，不知道可不可以给0，还是有别的处理
        # todo，另外我感觉average throughput是不是有点过大了，我测出来10的8次方，未知单位qwq
        for bps in current_client.bitrate_list:
            if bps <= bound_bitrate:
                selected_bitrate = bps

        # print(selected_bitrate)

        start_time = time.time()
        response = requests.get(f'{current_client.getURL()}/vod/{selected_bitrate}Seg{segment}-Frag{frag}', headers=ClientSelf.headerSelf)
        end_time = time.time()
        KB = float(response.headers['Content-Length']) * 8 / 1024
        # record the log message
        duration = end_time - start_time
        new_throughput = KB / duration

        current_client.throughput = ClientSelf.alpha * new_throughput + (1-ClientSelf.alpha) * current_client.throughput
        chunkname = str(segment) + "-" + str(frag)
        ClientSelf.record_log(start_time, duration, new_throughput, current_client.throughput, selected_bitrate, current_client.server_port, chunkname)
        return Response(response)
        # record the log message
    
    @staticmethod
    def record_log(cur_time, duration, tput, avg_tput, bitrate, server_port, chunkname):
        with open(ClientSelf.log_path, mode= "a", encoding='utf-8' ) as log:
            log.write(str(cur_time) + " " + str(duration) + " " + str(tput) + " " + str(avg_tput) + " "
                  + str(bitrate) + " " + str(server_port) + " " + chunkname + "\n")

    @staticmethod
    def request_dns() -> int:
        """
        Request dns server here.
        """
        # fixme:这里需要修改,需要把服务器中的port拿到
        response = requests.get("http://localhost:"+ClientSelf.dns_port + "/dnsRequest")
 
        return int(response.text) # 这个通过text可以直接把东西取出来
    
    @staticmethod
    @app.route('/qdanmu')
    def qdanmu():
        cookie = request.cookies
        cur_client_id = int(cookie.get("ID"))
        current_client = ClientSelf.dict_client.get(cur_client_id)
        to_return = ""
        for ele in current_client.danmulist_topush:
            to_return = to_return + str(ele) + "\r\n"
        current_client.danmulist_topush = []
        return make_response(to_return)

    @staticmethod
    @app.route('/sdanmu',methods = ['POST'])
    def sdanmu():
        danmu = request.stream.read().decode('utf-8')
        if danmu == "quit":
            shutdown_func = request.environ.get('werkzeug.server.shutdown')
            if shutdown_func is None:
                raise RuntimeError('Not running werkzeug')
            shutdown_func()
            return "Shutting down..."
        ClientSelf.history_danmu.append(danmu)
        for ele in ClientSelf.dict_client.keys():
            ClientSelf.dict_client.get(ele).danmulist_topush.append(danmu)
        return make_response("")

    # @staticmethod
    # @app.route('/postdanmu/<string:danmu>')
    # def sdanmu_from_get(danmu):
    #     ClientSelf.history_danmu.append(danmu)
    #     for ele in ClientSelf.dict_client.keys():
    #         ClientSelf.dict_client.get(ele).danmulist_topush.append(danmu)
    #     return make_response("")
        
        




if __name__ == '__main__':
    """
        argv[0] is the python file name.
        argv[1] is <log>, the path of file that logs the messages.
        argv[2] is <alpha>, [0, 1], in throughput estimate.
        argv[3] is <listen-port>, the TCP port your proxy should listen on for accepting connections from your browser.
        argv[4] is <dns-port>, UDP port DNS server listens on.
        argv[5] is [<default-port>], proxy should accept an optional argument specifying the port of the web server 
        from which it should request video chunks. If this argument is not present, 
        proxy should obtain the web server’s port by querying DNS server.
    """
    if len(sys.argv)>3:
        ClientSelf.log_path = sys.argv[1]
        with open(ClientSelf.log_path, mode= "w", encoding='utf-8' ) as log:
            log.seek(0)
            log.truncate()
        ClientSelf.alpha = float(sys.argv[2])
        ClientSelf.dns_port = sys.argv[4]
        app.run(host="localhost", port=int(sys.argv[3]))
    else: # 这个方便直接用vscodeDEBUG
        ClientSelf.log_path = "record.py"
        ClientSelf.alpha = 0.6
        ClientSelf.dns_port = "7775"
        app.run(host="localhost", port=7778)
