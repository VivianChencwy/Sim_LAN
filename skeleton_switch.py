from ee315_24_lib import SwitchFabric, Packet
import re

class Host:
    def __init__(self, mac, interface):
        """
        初始化主机对象。
        参数:
        - mac: 主机的MAC地址
        - interface: 主机连接的接口编号
        """
        # 检查MAC地址格式是否正确
        if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac):
            raise ValueError("Invalid MAC address format")
        self.mac = mac
        self.interface = interface
        self.buffer = []  # 用于存储接收到的数据包

    def send_packet(self, dst_mac, payload, switch):
        """
        发送数据包到交换机。
        参数:
        - dst_mac: 目标MAC地址
        - payload: 数据包内容
        - switch: 交换机对象
        """
        packet = Packet(src=self.mac, dst=dst_mac, payload=payload)  # 创建数据包
        switch.handle_packet(packet)  # 将数据包交给交换机处理

    def receive_packet(self, packet):
        """
        接收并处理从交换机转发来的数据包。
        参数:
        - packet: 数据包对象
        """
        if packet.dst == self.mac:  # 如果目标MAC地址匹配本主机
            self.buffer.append(packet)  # 将数据包存入缓冲区

class Switch:
    def __init__(self, fabric, num_interfaces=8):
        """
        初始化交换机。
        参数:
        - fabric: 交换结构对象
        - num_interfaces: 接口数量，默认为8
        """
        self.num_interfaces = num_interfaces
        self.interfaces = {i: None for i in range(self.num_interfaces)}  # 接口到主机的映射
        self.mac_table = {}  # MAC地址到接口的映射
        self.fabric = fabric  # 交换结构对象

    def handle_packet(self, packet):
        """
        处理数据包。
        参数:
        - packet: 数据包对象
        """
        # 学习源MAC地址
        if packet.src not in self.mac_table:
            self.mac_table[packet.src] = self.get_interface_by_mac(packet.src)

        # 查找目标MAC地址的接口
        dst_interface = self.mac_table.get(packet.dst)
        if dst_interface is not None:  # 如果找到目标接口
            self.fabric.forward_to_interface(packet, dst_interface)  # 转发到目标接口
        else:  # 如果目标接口未知
            # 向所有其他接口广播
            for interface, host in self.interfaces.items():
                if host and host.interface != self.get_interface_by_mac(packet.src):
                    self.fabric.forward_to_interface(packet, interface)

    def get_interface_by_mac(self, mac):
        """
        根据MAC地址获取接口编号。
        参数:
        - mac: MAC地址
        返回值:
        - 接口编号
        """
        for interface, host in self.interfaces.items():
            if host and host.mac == mac:
                return interface
        return None
