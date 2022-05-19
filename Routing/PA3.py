import sys
from queue import PriorityQueue


class Host:
    addr = ''
    edge = []
    weight = []
    idx = 0  # 将路由器和主机视作节点，宏观进行编号
    addr_map = {}  # 映射 相连节点 -> 与其相连接口地址
    pre_addr = ''  # 记录跑最短路的时候前一个节点的接口地址

    def __init__(self):
        self.addr = ''
        self.edge = []
        self.weight = []
        self.idx = 0
        self.addr_map = {}
        self.pre_addr = ''


class Router:
    addr = []
    edge = []
    weight = []

    idx = 0  # 将路由器和主机视作节点，宏观进行编号
    addr_map = {}  # 映射 相连节点 -> 与其相连接口地址
    pre_addr = ''  # 记录跑最短路的时候前一个节点的接口地址

    # 以下成员变量与计算 table 有关
    cost_map = {}  # 哈希表: 子网地址 -> 代价 （如果是直接相连代价就为0）
    table = []  # 最终的路由表
    gate_map = {}  # 哈希表: 子网区域 -> 经过接口（如果是直接相连就映射到自己的对应接口）

    def __init__(self):
        self.addr = []
        self.edge = []
        self.weight = []
        self.table = []
        self.idx = 0
        self.addr_map = {}
        self.pre_addr = ''

        # 以下成员变量与计算 table 有关
        self.cost_map = {}
        self.table = []
        self.gate_map = {}

    def print_table_info(self):
        print("Not implemented yet")


addr_list = []
router_list = []
host_list = []

addr_host_map = {}
addr_router_map = {}
edge_map = {}
edge_cost_map = {}

MAX_INT = sys.maxsize  # 获取极限最大值

# dijstra 算法计算路由最短路
def dijkstra(src: Host, dst: Host, flag:bool):
    number = len(router_list) + len(host_list)
    src_idx = src.idx
    src.pre_addr = '-1'

    # visited 数组标志已经被访问过的节点
    visited = []

    # 将距离数组初始化为 inf, 其中 src 到自己的距离初始化为 0
    dist = [MAX_INT] * number
    dist[src_idx] = 0

    # pq 优先队列
    pq = PriorityQueue()
    pq.put([0, src.addr])

    while not pq.empty():

        term = pq.get()  # 获取排在优先队列最开始，也就是距离最小的元素, 获取该元素的地址，通过地址找到对应 router 或者 host
        node_addr = term[1]
        # print("term = {}".format(term))
        # print("The node_addr = {}".format(node_addr))
        if node_addr in addr_host_map:
            node = addr_host_map[node_addr]
        else:
            node = addr_router_map[node_addr]

        node_idx = node.idx
        if node_idx in visited:
            continue
        visited.append(node_idx)
        edge_size = len(node.edge)

        for i in range(edge_size):
            # 获取所连接边的对应信息
            edge_node = node.edge[i]
            edge_weight = node.weight[i]
            edge_node_idx = edge_node.idx

            new_cost = dist[node_idx] + edge_weight
            if dist[edge_node_idx] > new_cost:
                dist[edge_node_idx] = new_cost

                edge_node.pre_addr = edge_node.addr_map[node] # 更新 pre 节点地址信息

                # print("edge_node_arr = {} and the new cost = {}".format(edge_node.addr, new_cost))
                if edge_node in host_list: # 如果节点是一个 host 类型
                    pq.put([new_cost, edge_node.addr])
                else: # 如果是一个 router 类型
                    pq.put([new_cost, edge_node.addr[0]])


    # 遍历添加路径列表
    start = dst
    paths = []
    next_node = addr_router_map[start.pre_addr]

    while start.pre_addr != '-1':
        if start.pre_addr in addr_router_map:
            next_node = addr_router_map[start.pre_addr]
            if next_node.addr_map[start] in addr_router_map:#两个都是 router # 更新路由表
                for key in start.cost_map:  # 对 node 的所有路由信息遍历
                    if (key not in next_node.cost_map) \
                            or (key in next_node.cost_map
                                and start.cost_map[key] + edge_cost_map[start.pre_addr] < next_node.cost_map[key]):  # 更新路由 table 信息条件
                        next_node.cost_map[key] = start.cost_map[key] + edge_cost_map[start.pre_addr]
                        next_node.gate_map[key] = start.addr_map[next_node].split('/')[0]

        else:
            next_node = addr_host_map[start.pre_addr]
            break

        paths.append(next_node.addr_map[start].split('/')[0])
        paths.append(start.pre_addr.split('/')[0])
        start = next_node

    paths.append(next_node.addr_map[start].split('/')[0])
    paths.append(src.addr.split('/')[0])

    if flag:
        # 将路径列表翻转之后输出
        paths.reverse()
        for path in paths:
            print(path, end=' ')
        print()
    else:
        return 0

# 路由聚合
def route_aggregation(router: Router) -> list:
    
    return router.table

    pass

# 计算子网 返回字符串(子网号)
def cal_subnet(string: str) -> str:
    info = string.split('/')
    addr = info[0]
    num = int(info[1]) # 子网掩码数字
    ex_num = num # 备份数字
    part_list = addr.split('.')
    res = ''
    for i in range(len(part_list)):
        part_num = int(part_list[i])
        if num < 8:
            mask = 255 << (8 - num)
            part_num = part_num & mask
        num = num - 8
        res = res + str(part_num)
        if i != len(part_list) - 1:
            res = res + '.'
    return res + '/' + str(ex_num)

# 从 cost_map 中添加最终路由 table 信息进 router 内部的 table
def add_table(router:Router):
    for key in router.cost_map:
        if router.cost_map[key] == 0:
            router.table.append(key + ' is directly connected')
        else:
            router.table.append(key + ' via ' + router.gate_map[key])

    router.table.sort()

    # print(router.table)




if __name__ == '__main__':
    # print(cal_subnet('200.30.5.0/22'))
    with open(sys.argv[1], 'r') as f:
        idx = 0
        for i in range(3):
            line = f.readline()
            if i == 0:  # 读取所有地址信息
                addr_list = line.split()
                # print(addr_list)
            elif i == 1:  # 处理路由器
                interface_list = line.split()  # 将所有路由器的地址分割成为一个个路由器的所有地址
                for interface in interface_list:
                    interface_in_router_list = interface.split(',')  # 将路由器的每一个地址分割出来
                    r = Router()
                    r.idx = idx
                    idx = idx + 1
                    for interface_in_router in interface_in_router_list:  # 遍历列表添加进路由器的 地址列表 当中
                        if interface_in_router[0] == '(':
                            r_addr = interface_in_router[2:-1]
                            r.addr.append(r_addr)
                            addr_router_map[r_addr] = r

                            r.cost_map[cal_subnet(r_addr)] = 0 # 添加子网信息，由于是自己连接的子网，所有 cost 为 0
                            r.gate_map[cal_subnet(r_addr)] = r_addr.split('/')[0]
                            # r.table.append(cal_subnet(r_addr)) # 直接往最终 table 添加子网信息

                        elif interface_in_router[0] == '\'' and interface_in_router[-1] == ')':
                            r_addr = interface_in_router[1:-2]
                            r.addr.append(r_addr)
                            addr_router_map[r_addr] = r

                            r.cost_map[cal_subnet(r_addr)] = 0 # 添加子网信息，由于是自己的端口，所有 cost 为 0
                            r.gate_map[cal_subnet(r_addr)] = r_addr.split('/')[0]
                            # r.table.append(cal_subnet(r_addr))  # 直接往最终 table 添加子网信息
                        else:
                            r_addr = interface_in_router[1:-1]
                            r.addr.append(r_addr)
                            addr_router_map[r_addr] = r

                            r.cost_map[cal_subnet(r_addr)] = 0  # 添加子网信息，由于是自己的端口，所有 cost 为 0
                            r.gate_map[cal_subnet(r_addr)] = r_addr.split('/')[0]
                            # r.table.append(cal_subnet(r_addr))  # 直接往最终 table 添加子网信息

                    router_list.append(r)

                # 将剩下的地址映射到 host 当中
                for address in addr_list:
                    if address not in addr_router_map:
                        host = Host()
                        host.idx = idx
                        idx = idx + 1
                        host.addr = address
                        host_list.append(host)
                        addr_host_map[address] = host
            else:
                edge_list = line.split()  # 获取每一条边的所有信息
                for edge in edge_list:  # 遍历每一条边
                    edge_part = edge.split(',')
                    from_node = ''
                    to_node = ''
                    w = 0
                    for part in edge_part:  # 遍历一条边的所有信息
                        if part[0] == '(':  # from_node
                            from_node = part[2:-1]
                        elif part[0] == '\'':
                            to_node = part[1:-1]
                        else:
                            w = int(part[0:-1])
                    edge_map[from_node] = to_node
                    edge_map[to_node] = from_node
                    # 记录边对应的 weight 信息
                    edge_cost_map[from_node] = w
                    edge_cost_map[to_node] = w
                    # print("from_node = {}".format(from_node))
                    # print("to_node = {}".format(to_node))
                    # 建图(三种可能的情况判断)
                    if from_node in addr_host_map and to_node in addr_router_map:

                        from_host = addr_host_map[from_node]
                        to_router = addr_router_map[to_node]

                        # 映射对应地址，便于之后最短路映射对应接口地址
                        from_host.addr_map[to_router] = to_node
                        to_router.addr_map[from_host] = from_node

                        from_host.edge.append(to_router)
                        from_host.weight.append(w)
                        to_router.edge.append(from_host)
                        to_router.weight.append(w)
                        # print("now {}'s edge contains ".format(from_host.addr))
                        # for edge in from_host.edge:
                        #     print(edge.addr)
                        #
                        # print("now {}'s edge contains ".format(to_router.addr))
                        # for edge in to_router.edge:
                        #     print(edge.addr)

                    elif from_node in addr_router_map and to_node in addr_router_map:

                        from_router = addr_router_map[from_node]
                        to_router = addr_router_map[to_node]

                        # 映射地址
                        from_router.addr_map[to_router] = to_node
                        to_router.addr_map[from_router] = from_node

                        from_router.edge.append(to_router)
                        from_router.weight.append(w)
                        to_router.edge.append(from_router)
                        to_router.weight.append(w)
                        # print("now {}'s edge contains ".format(from_router.addr))
                        # for edge in from_router.edge:
                        #     print(edge.addr)
                        #
                        # print("now {}'s edge contains ".format(to_router.addr))
                        # for edge in to_router.edge:
                        #     print(edge.addr)

                    elif from_node in addr_router_map and to_node in addr_host_map:

                        from_router = addr_router_map[from_node]
                        to_host = addr_host_map[to_node]

                        # 映射地址
                        from_router.addr_map[to_host] = to_node
                        to_host.addr_map[from_router] = from_node

                        to_host.edge.append(from_router)
                        to_host.weight.append(w)
                        from_router.edge.append(to_host)
                        from_router.weight.append(w)
                        # print("now {}'s edge contains ".format(from_router.addr))
                        # for edge in from_router.edge:
                        #     print(edge.addr)
                        #
                        # print("now {}'s edge contains ".format(to_host.addr))
                        # for edge in to_host.edge:
                        #     print(edge.addr)
                    else:
                        print("In building graph, the condition is not taken into consideration")
        ''' 检验建图是否正确
        for host in host_list:
            print("host_id = {}".format(host.idx))
            for edge in host.edge:
                print(edge.addr)

        for router in router_list:
            print("router_id = {}".format(router.idx))
            for edge in router.edge:
                print(edge.addr)
        '''

        case_num = int(f.readline())
        for i in range(case_num):
            line = f.readline()
            test_info = line.split()
            if test_info[0] == 'PATH':  # 如果是 PATH, 则接收两个 host 端口
                src = addr_host_map[test_info[1]]
                dst = addr_host_map[test_info[2]]

                # 运行 dijkstra 算法
                for src_host in host_list:
                    for dst_host in host_list:
                        if dst_host != src_host:
                            dijkstra(src_host, dst_host, False)


                dijkstra(src, dst, True)

                for router in router_list:
                    add_table(router)

                    for item in router.table:
                        print(item)
                    print("After")


            else:  # 如果是 TABLE, 则接收一个路由器的端口信息进行映射
                router_tested = addr_router_map[test_info[1].split(',')[0][2:-1]]
                router_tested.print_table_info()
