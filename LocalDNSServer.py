import threading
from dns import resolver, rdatatype
import socket

from dns.resolver import NoNameservers
from dnslib import DNSRecord, QTYPE, RD, SOA, DNSHeader, RR, A, CNAME
"""
clue about multithread:
many dns server thread and each one get dns query, resolve the query and build response.you may put the result into a 
send_queue
a receiver thread that used to receive message from client and distribute message to dns server, you may put it into a 
queue
a sender thread to send dns resolving result back to client
attention that in some system, socket is not thread safe, you may need thread lock
don't forget thread safe in your cache if needed cause many thread will access it
"""



class CacheManager:
    # NOTE: class that manage cache.
    def __init__(self):
        # TODO
        self.content = []

    def readCache(self, domain_name):
        # TODO: how you read from cache
        raise NotImplementedError

    def writeCache(self, domain_name, response):
        # TODO: how you write to cache
        raise NotImplementedError


class ReplyGenerator:
    # NOTE: While cannot resolve the corresponding ip or domain name is not found you should send message like this
    #  type.
    @staticmethod
    def replyForNotFound(income_record):
        """
        :param income_record: the income dns record from dig
        :return: the reply record
        """
        header = DNSHeader(id=income_record.header.id, bitmap=income_record.header.bitmap, qr=1)
        header.set_rcode(0)  # 3 DNS_R_NXDOMAIN, 2 DNS_R_SERVFAIL, 0 DNS_R_NOERROR
        record = DNSRecord(header, q=income_record.q)
        return record

    # NOTE: You should implement your reply here
    @staticmethod
    def myReply(income_record):
        # TODO: build your reply here
        raise NotImplementedError
        return record

    # NOTE: This is an example for the reply message with just one rr record of a type.
    @staticmethod
    def replyForA(income_record, ip, ttl=None):
        """
        :param income_record: the income dns record from dig
        :param ip: the founded domain ip
        :param ttl: time to live
        :return: the reply record
        """
        r_data = A(ip)
        header = DNSHeader(id=income_record.header.id, bitmap=income_record.header.bitmap, qr=1)
        domain = income_record.q.qname
        query_type_int = QTYPE.reverse.get('A') or income_record.q.qtype
        record = DNSRecord(header, q=income_record.q, a=RR(domain, query_type_int, rdata=r_data, ttl=ttl))
        return record


class DNSServer:
    """
    In this class, you need to implement several methods which set up your
    local DNS server,such as receive, query, reply and others you need
    """

    def __init__(self, source_ip, source_port, ip='127.0.0.1', port=5533):
        self.source_ip = source_ip
        self.source_port = source_port
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.cache_manager = CacheManager()
        self.dns_handler = DNSHandler(self.source_ip, self.source_port, self.cache_manager)

    def start(self):
        while True:
            message, address = self.receive()
            response = self.dns_handler.handle(message)


            self.reply(address,response)

    def receive(self):
        return self.socket.recvfrom(8192)

    def reply(self, address,response):
        self.socket.sendto(response.pack(), address)


class DNSHandler(threading.Thread):
    """
    In this class, you need to implement several methods which provide strategies
    for your DNS server, such as handle, query and others you need

    """

    def __init__(self, source_ip, source_port, cache_manager):
        super().__init__()
        self.source_ip = source_ip
        self.source_port = source_port
        self.LOCAL_DNS_SERVER_IP = '8.8.8.8'
        self.DNS_SERVER_PORT = 53
        self.cache_manager = cache_manager




    def handle(self, message):
        """
        :param message: dns message from dig
        """
        try:
            income_record = DNSRecord.parse(message)

        except:
            return
        #TODO: initialize your variable here
        domain_name = str(income_record.q.qname).strip('.') # 获取域名 —— www.baidu.com


        # if 存储在本地的cache当中就直接返回
        # else query ROOT server
        # query ROOT server with domain_name:


        response = None

        raise NotImplementedError
        # TODO: you need to implement how your handle a dns query like how to access the cache and choose the
        #  correct respones

        return response


        # NOTE: this method is a basic use case of library dnspyhton. and it use it to get one root dns server's name and ip
    def query(self, query_name, source_ip, source_port):
        """
        Whole iterative process.
        Firstly get IP address of root server, √
        then enter into a loop until get response whose answer type is A.
        :param query_name:
        :param source_ip:
        :param source_port:
        :return: response: RRSet of all true A type answers
                cname: if cname not exists, returns None
        """
        # Instantiate dns.resolver.Resolver and set flag (value of recursion desired) as 0.
        dns_resolver = resolver.Resolver()

        dns_resolver.flags = 0X0000 # 迭代查询标志

        # Get IP address of root server
        server_ip, server_name = self.queryRoot(source_ip, source_port)
        server_port = self.DNS_SERVER_PORT

        # 向根服务器查询TLD服务器
        dns_resolver.nameservers = [server_ip] # 指定要查询的目标DNS服务器IP地址为根DNS服务器
        answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip, # 根据根服务器IP查找 domain_name
                                      raise_on_no_answer=False, source_port=source_port)
        response = answer.response # 获得了根服务器的回复报文
        print("In query method, the response from root server is ")
        print(response)

        # print("The response.additional[0] is")
        # print(response.additional[0])


        # tld_ip = response.additional[0][0].to_text()
        # tld_name = response.additional[0].name

        # print("The authority_ip is")
        # print(tld_ip)
        #
        # print("The authority name is ")
        # print(tld_name)

        # 把所有顶级域作为下一次查询的服务器
        dns_resolver.nameservers = []

        for rr in response.additional:
            dns_resolver.nameservers.append(rr[0].to_text())
            # print(rr[0].to_text())

        answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip,  # 根据根服务器IP查找 domain_name
                                      raise_on_no_answer=False, source_port=source_port)
        response = answer.response  # 获得了TLD服务器的回复报文


        print("The response message from TLD is ")
        print(response)

        # 通过TLD 的报文获得权威服务器的 IP 和名字
        # authority_ip = response.additional[0][0].to_text()
        # authority_name = response.additional[0].name

        # 将所有权威服务器的IP作为下次查询的服务器
        dns_resolver.nameservers = []
        for rr in response.additional:
            for i in rr:
                dns_resolver.nameservers.append(i.to_text())

        # 向权威服务器发送请求
        print("In line 216, query_name is")
        print(query_name)

        return self.dfs(query_name=query_name, source_ip=source_ip, source_port=source_port, dns_resolver=dns_resolver)

        # TODO: you need complete how your write your code here




        # raise NotImplementedError

    def dfs(self, source_ip, source_port, query_name, dns_resolver):
        print("In line 230")
        print(dns_resolver.nameservers)
        try:
            answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip,  # 根据根服务器IP查找 domain_name
                                      raise_on_no_answer=False, source_port=source_port)
        except:
            print("In except")
            return self.query(query_name=query_name, source_ip=source_ip, source_port=source_port)

        response = answer.response  # 获得权威服务器的回复报文

        print("The response from authority server is ")
        print(response)
        # print(response.answer[0].rdtype)

        if response.answer != [] and response.answer[0].rdtype == 1:  # 如果可以直接得到A类型信息，就直接返回
            print("The target ip = ")
            print(response.answer[0][0].to_text())
            target_ip = response.answer[0][0].to_text()
            target_name = response.answer[0].name
            return target_ip, target_name

        elif response.answer != [] and response.answer[0].rdtype == rdatatype.CNAME:
            query_name = response.answer[0][0].to_text()
            print("Now query_name = ")
            print(query_name)

            return self.dfs(query_name=query_name, source_ip=source_ip, source_port=source_port, dns_resolver=dns_resolver)



        print("now query_name = ")
        print(query_name)
        # 使用规范主机名再进行A类型查询
        if answer.response.additional != []:
            dns_resolver.nameservers = []
            for rr in answer.response.additional:
                dns_resolver.nameservers.append(rr[0].to_text())
            return self.dfs(query_name=query_name, source_ip=source_ip, source_port=source_port, dns_resolver=dns_resolver)

        if answer.response.authority != []:
            name = query_name
            query_name = response.authority[0][0].to_text()
            print("In authority, query_name = ")
            print(query_name)
            authority_ip, authority_name = self.query(query_name= query_name, source_ip=source_ip, source_port=source_port)
            query_name = name
            dns_resolver.nameservers = [authority_ip]
            return self.dfs(query_name=query_name, source_ip=source_ip, source_port=source_port, dns_resolver=dns_resolver)


        answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip,
                                      raise_on_no_answer=False, source_port=source_port)
        ''' 
        try:
            print("In try ")
            answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip,
                                      raise_on_no_answer=False, source_port=source_port)
        except NoNameservers:
            print("In catch ")
            self.query(query_name=query_name, source_ip=source_ip, source_port=source_port)
            return
        '''

        response = answer.response  # 用规范主机名获得权威服务器的回复报文

        print("The response from authority server2 is ")
        print(response)

        # 如果得不到答案就重复询问直到得到答案为止
        while response.answer == []:
            # print("In loop, response = ")
            # print(response)
            dns_resolver.nameservers = []
            for rr in response.additional:
                dns_resolver.nameservers.append(rr[0].to_text())
            answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip,
                                          raise_on_no_answer=False, source_port=source_port)
            response = answer.response

        target_ip = response.answer[0][0].to_text()
        target_name = response.answer[0].name
        print("target_ip = ")
        print(target_ip)
        return target_ip, target_name



    def queryRoot(self, source_ip, source_port):
        """
        Query IP address and name of root DNS server.
        :param source_ip: source IP address of query
        :param source_port: source port number of query
        :return: server_ip, server_name
        """
        # Instantiate dns.resolver.Resolver and set flag (value of rd) as 0.
        dns_resolver = resolver.Resolver()
        dns_resolver.flags = 0X0000
        # Set initial IP name, address and port number.
        server_name = 'Local DNS Server'
        server_ip = self.LOCAL_DNS_SERVER_IP
        server_port = self.DNS_SERVER_PORT
        # Set nameservers of dns_resolver as list of IP address of server.
        dns_resolver.nameservers = [server_ip]

        # Use dns_resolver to query name of root server and receive response.
        answer = dns_resolver.resolve(qname='', rdtype=rdatatype.NS, source=source_ip, raise_on_no_answer=False,
                                      source_port=source_port)
        response = answer.response
        query_name = response.answer[0][0].to_text()

        # Use dns_resolver to query address of root server and receive response.
        answer = dns_resolver.resolve(qname=query_name, rdtype=rdatatype.A, source=source_ip,
                                      raise_on_no_answer=False, source_port=source_port)
        response = answer.response
        # print("in querying the root server, the response answer is")
        # print(response.answer)
        server_ip = response.answer[0][0].to_text()
        server_name = response.answer[0].name

        return server_ip, server_name

if __name__ == '__main__':
    source_ip = input('Enter your ip: ')
    source_port = input('Enter your port: ')
    source_ip = str(source_ip)
    source_port = int(source_port)
    local_dns_server = DNSServer(source_ip, source_port)

    dns_handler = DNSHandler(None, None, None)
    root_sever_ip, root_severs = dns_handler.queryRoot(source_ip=source_ip, source_port=source_port)
    print(root_sever_ip)
    print(root_severs)

    dns_handler.query("www.sina.com", source_ip=source_ip, source_port=source_port)

    # local_dns_server.start()
