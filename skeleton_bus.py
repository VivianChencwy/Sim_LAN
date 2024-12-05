import re
from ee315_24_lib import Bus, Packet

class Host:
    def __init__(self, mac):
        """
        初始化主机对象，校验并设置MAC地址。
        参数:
        - mac: 主机的MAC地址
        """
        # 验证MAC地址格式是否有效
        if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac):
            raise ValueError("Invalid MAC address format")
        self.mac = mac  # 主机的MAC地址
        self.buffer = []  # 用于存储接收到的数据包的缓冲区

    def send_packet(self, dst_mac, payload, bus):
        """
        发送数据包到总线。
        参数:
        - dst_mac: 目标MAC地址
        - payload: 数据包的内容
        - bus: 总线对象
        """
        # 创建数据包对象
        packet = Packet(src=self.mac, dst=dst_mac, payload=payload)
        # 调用总线的广播功能发送数据包
        bus.broadcast(packet)

    def receive_packet(self, packet):
        """
        接收并处理从总线发送的数据包。
        参数:
        - packet: 接收到的数据包对象
        """
        # 检查数据包的目标地址是否匹配主机的MAC地址
        if packet.dst == self.mac:
            # 如果匹配，将数据包存储到缓冲区
            self.buffer.append(packet)

# 测试代码
if __name__ == "__main__":
    bus = Bus()
    # 创建三个主机对象
    host1 = Host("00:00:00:00:00:01")
    host2 = Host("00:00:00:00:00:02")
    host3 = Host("00:00:00:00:00:03")

    # 将主机连接到总线
    bus.connect_host(host1)
    bus.connect_host(host2)
    bus.connect_host(host3)

    # 主机之间发送数据包
    host1.send_packet("00:00:00:00:00:02", "Hello from host1", bus)
    host2.send_packet("00:00:00:00:00:03", "Hello from host2", bus)
    host3.send_packet("00:00:00:00:00:01", "Hello from host3", bus)
