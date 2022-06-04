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

    aggre_table = []

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

        self.aggre_table = []

    def print_table_info(self):
        for info in self.table:
            print(info)
        print("After")
        for info in self.aggre_table:
            print(info)



addr_list = []
router_list = []
host_list = []

addr_host_map = {}
addr_router_map = {}
edge_map = {}
edge_cost_map = {}

MAX_INT = sys.maxsize  # 获取极限最大值

# dijstra 算法计算路由最短路
def dijkstra(src, dst: Host, flag:bool):
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
    if src in router_list:
        pq.put([0, src.addr[0]])
    else:
        pq.put([0, src.addr])

    while not pq.empty():

        term = pq.get()  # 获取排在优先队列最开始，也就是距离最小的元素, 获取该元素的地址，通过地址找到对应 router 或者 host
        node_addr = term[1]

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

                if edge_node in host_list: # 如果节点是一个 host 类型
                    pq.put([new_cost, edge_node.addr])
                else: # 如果是一个 router 类型
                    pq.put([new_cost, edge_node.addr[0]])


    # 遍历添加路径列表, 之前的版本默认起点是主机，但是事实上都有可能
    start = dst
    paths = []
    next_node = addr_router_map[start.pre_addr]

    pre_start = start

    while start.pre_addr != '-1':
        if start.pre_addr in addr_router_map:
            next_node = addr_router_map[start.pre_addr] # 其实是前一个节点
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
        pre_start = start
        start = next_node

    if src in host_list:
        paths.append(next_node.addr_map[start].split('/')[0])
    else:
        paths.append('0')

    if src in router_list:
        for key in src.cost_map:  # 对 node 的所有路由信息遍历
            if (pre_start in router_list):

                if (key not in src.cost_map) \
                    or (key in pre_start.cost_map
                        and pre_start.cost_map[key] + edge_cost_map[pre_start.pre_addr] < src.cost_map[
                            key]):  # 更新路由 table 信息条件
                    src.cost_map[key] = pre_start.cost_map[key] + edge_cost_map[pre_start.pre_addr]
                    src.gate_map[key] = pre_start.addr_map[src].split('/')[0]
        paths.append('0')
    else:
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
def route_aggregation(router: Router):

    interface_map = {} # 映射：发送接口 -> 子网列表[]

    for key in router.cost_map: # key example: 67.100.3.8/24
        if router.cost_map[key] == 0:
            continue
        interface_addr = router.gate_map[key] # 发送接口的地址 example: 67.100.3.3/24
        if interface_addr not in interface_map:
            interface_map[interface_addr] = []
            interface_map[interface_addr].append(key)
        else:
            interface_map[interface_addr].append(key)

    aggre_map = {} # 映射：前16位子网号 -> 具体子网号列表
    for key in interface_map:
        net_list = interface_map[key]
        for net in net_list: # net example: 67.100.3.8/24
            # 提取出前 16 位
            base_list = net.split('.')
            base = base_list[0] + '.' + base_list[1] # base example: 67.100
            if base not in aggre_map:
                aggre_map[base] = []
                aggre_map[base].append(net)
            else:
                aggre_map[base].append(net)

    # 对同一块 base 里面的地址做路由聚合
    for key in aggre_map:
        if len(aggre_map[key]) >= 2:
            # 提取最长公共前缀长度

            lng_part1 = int(aggre_map[key][0].split('.')[2])
            lng_part2 = int(aggre_map[key][0].split('.')[3].split('/')[0])

            longest_num = int(aggre_map[key][0].split('.')[3].split('/')[1])


            for net in aggre_map[key]:
                cnt = 16
                part1 = int(net.split('.')[2])
                part2 = int(net.split('.')[3].split('/')[0])

                # 比较第一部分 (part1 and lng_part1)
                mask = 128 # 8'b10000000
                aggre_num = 0 # 第三部分的子网段
                continue_flag = True # 表示是否需要进行第二部分的比较
                for i in range(8):
                    lng_num = mask & lng_part1
                    num = mask & part1
                    if lng_num == num:
                        aggre_num = aggre_num + pow(2, 7-i) * (num >> 7)
                        cnt = cnt + 1
                    else:
                        continue_flag = False
                        break
                    lng_part1 = lng_part1 << 1
                    part1 = part1 << 1

                aggre_num2 = 0 # 第四部分的子网段
                # 如果需要的话，比较第二部分(part2 and lng_part2)
                if continue_flag:
                    for i in range(8):
                        lng_num = mask & lng_part2
                        num = mask & part2
                        if lng_num == num:
                            aggre_num2 = aggre_num2 + pow(2, 8 - i) * (num >> 7)
                            cnt = cnt + 1
                        else:
                            break
                        lng_part2 = lng_part2 << 1
                        part2 = part2 << 1

                longest_num = min(cnt, longest_num)
                lng_part1 = aggre_num
                lng_part2 = aggre_num2

            res_str = aggre_map[key][0].split('.')[0] +'.'+ aggre_map[key][0].split('.')[1] + '.' + str(lng_part1) + '.' + str(lng_part2) + '/' + str(longest_num)
            aggre_map[key] = [res_str]


    cnt = 0
    for key in router.cost_map:
        cnt = cnt + 1
        if router.cost_map[key] == 0:
            router.aggre_table.append(key + ' is directly connected')
        else:
            out_interface = router.gate_map[key] # 发送接口
            for net in interface_map[out_interface]:
                base_list = net.split('.')
                base = base_list[0] + '.' + base_list[1]
                info = aggre_map[base][0] + ' via ' + out_interface
                if info not in router.aggre_table:
                    router.aggre_table.append(aggre_map[base][0] + ' via ' + out_interface)

    router.aggre_table.sort()


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

                    else:
                        print("In building graph, the condition is not taken into consideration")

        # 运行 dijkstra 算法
        for router in router_list:
            for dst_host in host_list:
                dijkstra(router, dst_host, False)

        for router in router_list:
            add_table(router)
            route_aggregation(router)


        # print('Test for router')
        # for router in router_list:
        #     print("new router")
        #
        #     router.print_table_info()
        # print('-------------------------------------')




        case_num = int(f.readline())
        for i in range(case_num):
            line = f.readline()
            test_info = line.split()
            if test_info[0] == 'PATH':  # 如果是 PATH, 则接收两个 host 端口
                src = addr_host_map[test_info[1]]
                dst = addr_host_map[test_info[2]]

                dijkstra(src, dst, True)

            else:  # 如果是 TABLE, 则接收一个路由器的端口信息进行映射
                router_tested = addr_router_map[test_info[1].split(',')[0][2:-1]]

                router_tested.print_table_info()
