import asyncio

keys = ('method', 'path', 'Range')

import sys
danmakus = []

class HTTPHeader:
    """
        HTTPHeader template, you can use it directly
    """

    def __init__(self):
        self.headers = {key: None for key in keys}
        self.version = '1.0 '
        self.server = 'Tai'
        self.contentLength = None
        self.contentRange = None
        self.contentType = None
        self.location = None
        self.range = None
        self.state = None
        # sys.stderr.write("构造一个 HttpHeader 对象\n")

    def parse_header(self, line):
        # sys.stderr.write("读入{{{}}}，并解析。\n".format(line))
        fields = line.split(' ')
        if fields[0] == 'GET' or fields[0] == 'POST' or fields[0] == 'HEAD':
            self.headers['method'] = fields[0]
            self.headers['path'] = fields[1]
            sys.stderr.write("method: {}\t path: {}\n".format(fields[0], fields[1])) 
        fields = line.split(':', 1)
        if fields[0] == 'Range':
            start, end = (fields[1].strip().strip('bytes=')).split('-')
            self.headers['Range'] = start, end

    def set_version(self, version):
        self.version = version
        # sys.stderr.write("设置版本：{}\n".format(version))

    def set_location(self, location):
        self.location = location
        # sys.stderr.write("设置location: {}\n".format(location))

    def set_state(self, state):
        self.state = state
        # sys.stderr.write("设置state: {}\n".format(state))

    def set_info(self, contentType, contentRange):
        self.contentRange = contentRange
        self.contentType = contentType
        # sys.stderr.write("设置 info ... ")

    def set_range(self):
        start, end = self.headers['Range']
        contentRange = int(self.contentRange)
        if start == '':
            end = int(end)
            start = contentRange - end
            end = contentRange - 1
        if end == '':
            end = contentRange - 1
        start = int(start)
        end = int(end)
        self.contentLength = str(end - start + 1)
        self.range = (start, end)
        # sys.stderr.write("self.range = {}\n".format(self.range))

    def get(self, key):
        # sys.stderr.write("get(self, key={}) is invoked. ".format(key))
        return self.headers.get(key)

    @property
    def method(self): 
        return self.headers['method']
    
    @property
    def path(self):
        return self.headers['path']

    def message(self):  # Return response header (响应报文)
        return 'HTTP/' + self.version + self.state + '\r\n' \
               + ('Content-Length:' + self.contentLength + '\r\n' if self.contentLength else '') \
               + ('Content-Type:' + 'text/html' + '; charset=utf-8' + '\r\n' if self.contentType else '') \
               + 'Server:' + self.server + '\r\n' \
               + ('Accept-Ranges: bytes\r\n' if self.range else '') \
               + ('Content-Range: bytes ' + str(self.range[0]) + '-' + str(
                self.range[1]) + '/' + self.contentRange + '\r\n' if self.range else '') \
               + ('Location: ' + self.location + '\r\n' if self.location else '') \
               + 'Connection: close\r\n'  + 'Access-Control-Allow-Origin: * \r\n' \


async def dispatch(reader, writer):
    # Use reader to receive HTTP request
    # Writer to send HTTP response
    # sys.stderr.write("开启一个 dispatch 方法\n") 
    httpHeader = HTTPHeader()
    while True:
        data = await reader.readline()
        print(data)
        message = data.decode()
        
        httpHeader.parse_header(message)
        # print(httpHeader.message)
        if data == b'\r\n' or data == b'':
            break
    if httpHeader.method == 'GET':
        httpHeader.set_state('200 OK')
        print("receive GET")
        print(httpHeader.path)
        if httpHeader.path == '/': 
            print("In path...")
            writer.write(httpHeader.message().encode(encoding='utf-8'))  # construct 200 OK HTTP header
            html_page = open("danmu.html", encoding='utf-8')
            contents = html_page.readlines()  
            homepage = ''
            for e in contents:
                homepage += e 
            writer.write(homepage.encode())  # Response for GET PAGE (写入页面)
        elif httpHeader.path == '/NEWDANMAKUS':
            print("In new Danmakus") 
        elif httpHeader.path == '/favicon.ico':
            pass
             
        else: 
            assert False 
        # TODO: handle get request with different situation: GET PAGE and GET NEWDANMAKUS
    elif httpHeader.get('method') == 'POST':
        # TODO: handle post request with given parameters
        print("receive POST")
        httpHeader.set_state('200 OK')
        writer.write(httpHeader.message().encode(encoding='utf-8'))  # construct 200 OK HTTP header

    
    writer.close()


if __name__ == '__main__':
    port = 8765
    loop = asyncio.get_event_loop()
    co_ro = asyncio.start_server(dispatch, '127.0.0.1', port, loop=loop)
    server = loop.run_until_complete(co_ro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
