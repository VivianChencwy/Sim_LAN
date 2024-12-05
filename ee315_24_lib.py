from queue import Queue

# 定义总线类，用于模拟主机间的广播通信
class Bus:
    def __init__(self):
        # 初始化总线主机列表
        self.hosts = []
        # 初始化总线日志文件
        self.log_file = "bus_log.txt"
        # 写入日志文件初始内容
        with open(self.log_file, 'w') as f:
            f.write("Bus Log Started\n")
        # 记录总线初始化事件
        self.log_event("Bus initialized")

    # 日志记录方法
    def log_event(self, message, category="INFO"):
        """
        记录事件日志到日志文件。
        参数:
        - message: 事件描述
        - category: 日志类别（默认 "INFO"）
        """
        with open(self.log_file, 'a') as f:
            f.write(f"[{category}] {message}\n")

    # 主机连接到总线
    def connect_host(self, host):
        """
        将主机连接到总线，并记录日志。
        参数:
        - host: 主机对象
        """
        self.hosts.append(host)  # 将主机添加到主机列表
        self.log_event(f"Host {host.mac} connected to bus")  # 记录连接事件

    # 广播数据包
    def broadcast(self, packet):
        """
        广播数据包到所有连接的主机（排除发送者）。
        参数:
        - packet: 数据包对象
        """
        self.log_event(f"Broadcasting packet: {packet}")  # 记录广播事件
        for host in self.hosts:  # 遍历所有已连接的主机
            if host.mac != packet.src:  # 排除数据包的发送者
                host.receive_packet(packet)  # 调用主机的接收方法

# 定义数据包类，用于表示网络传输的基础单元
class Packet:
    def __init__(self, src, dst, payload):
        """
        初始化数据包。
        参数:
        - src: 源地址（MAC 地址）
        - dst: 目标地址（MAC 地址）
        - payload: 数据内容
        """
        self.src = src  # 源 MAC 地址
        self.dst = dst  # 目标 MAC 地址
        self.payload = payload  # 数据包的有效载荷

    def __str__(self):
        """
        定义数据包的字符串表示形式。
        """
        return f"Packet(src={self.src}, dst={self.dst}, payload={self.payload})"

# 定义交换结构类，用于模拟网络交换机
class SwitchFabric:
    def __init__(self):
        """
        初始化交换结构，包括队列和接口映射表。
        """
        self.queue = Queue()  # 数据包队列
        self.physical_map = {}  # 接口到 MAC 地址的映射表
        self.interfaces = {}  # 接口到主机的映射表
        self.log_file = "fabric_log.txt"  # 初始化日志文件
        with open(self.log_file, 'w') as f:
            f.write("Switch Fabric Log Started\n")
        self.log_event("Switch Fabric initialized")  # 记录初始化事件

    # 日志记录方法
    def log_event(self, message, category="INFO"):
        """
        记录事件日志到日志文件。
        参数:
        - message: 事件描述
        - category: 日志类别（默认 "INFO"）
        """
        with open(self.log_file, 'a') as f:
            f.write(f"[{category}] {message}\n")

    # 将主机连接到交换机
    def connect_host_to_switch(self, host, switch):
        """
        将主机通过接口连接到交换机。
        参数:
        - host: 主机对象
        - switch: 交换机对象
        """
        switch.interfaces[host.interface] = host  # 接口到主机的映射
        self.physical_map[host.interface] = host.mac  # 接口到 MAC 地址的映射
        self.interfaces[host.interface] = host  # 接口到主机的映射

    # 将数据包转发到指定接口
    def forward_to_interface(self, packet, interface):
        """
        将数据包转发到特定接口。
        参数:
        - packet: 数据包对象
        - interface: 接口编号
        """
        if interface in self.interfaces:  # 检查接口是否有效
            self.interfaces[interface].receive_packet(packet)  # 调用主机的接收方法
            self.log_event(f"Packet forwarded - Interface: {interface}, {packet}", f"SWITCH->{interface}")  # 记录转发事件
        else:
            self.log_event(f"Forward failed - Invalid interface: {interface}", "ERROR")  # 记录错误日志

    # 根据目标地址转发数据包
    def forward_to_switch(self, packet):
        """
        查找目标地址对应的接口并转发数据包。
        参数:
        - packet: 数据包对象
        返回值:
        - src_interface: 源接口
        - packet: 数据包对象
        """
        dst_interface = 0  # 初始化目标接口
        # 查找目标 MAC 地址对应的接口
        if packet.dst in self.physical_map.values():
            for interface, mac in self.physical_map.items():
                if mac == packet.dst:
                    dst_interface = interface
                    break

        src_interface = 0  # 初始化源接口
        # 查找源 MAC 地址对应的接口
        if packet.dst in self.physical_map.values():
            for interface, mac in self.physical_map.items():
                if mac == packet.src:
                    src_interface = interface
                    break

        # 记录转发事件
        self.log_event(f"{packet} forwarded to switch", f"SWITCH@{dst_interface}")
        return src_interface, packet  # 返回源接口和数据包

    # 数据包日志记录
    def log_packet(self, message):
        """
        记录数据包的日志信息。
        参数:
        - message: 日志描述
        """
        with open(self.log_file, 'a') as f:
            f.write(f"{message}\n")
