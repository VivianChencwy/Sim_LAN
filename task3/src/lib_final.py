from queue import Queue
class Bus:
    def __init__(self):
        self.hosts = []
        self.log_file = "bus_log.txt"
        with open(self.log_file, 'w') as f:
            f.write("Bus Log Started\n")
        self.log_event("Bus initialized")

    def log_event(self, message, category="INFO"):
        with open(self.log_file, 'a') as f:
            f.write(f"[{category}] {message}\n")

    def connect_host(self, host):
        self.hosts.append(host)
        self.log_event(f"Host {host.mac} connected to bus")

    def broadcast(self, packet):
        self.log_event(f"Broadcasting packet: {packet}")
        for host in self.hosts:
            if host.mac != packet.src:
                host.receive_packet(packet)

class Packet:
    def __init__(self, src, dst, src_ip, dst_ip, payload, vlan_id=1):
        """
        初始化数据包。
        参数:
        - src: 源MAC地址
        - dst: 目标MAC地址
        - src_ip: 源IP地址
        - dst_ip: 目的IP地址
        - payload: 数据内容
        - vlan_id: VLAN ID（默认为1）
        """
        self.src = src
        self.dst = dst
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.payload = payload
        self.vlan_id = vlan_id

    def __str__(self):
        return f"Packet(src={self.src}, dst={self.dst}, src_ip={self.src_ip}, dst_ip={self.dst_ip}, payload={self.payload}, vlan_id={self.vlan_id})"

class SwitchFabric:
    def __init__(self):
        self.queue = Queue()
        self.physical_map = {}
        self.interfaces = {}
        self.vlan_map = {}
        self.log_file = "fabric_log.txt"
        with open(self.log_file, 'w') as f:
            f.write("Switch Fabric Log Started\n")
        self.log_event("Switch Fabric initialized")

    def log_event(self, message, category="INFO"):
        with open(self.log_file, 'a') as f:
            f.write(f"[{category}] {message}\n")

    def connect_host_to_switch(self, host, switch):
        switch.interfaces[host.interface] = host
        self.physical_map[host.interface] = host.mac
        self.interfaces[host.interface] = host

    def forward_to_interface(self, packet, interface):
        if interface in self.interfaces:
            self.interfaces[interface].receive_packet(packet)
            self.log_event(f"Packet forwarded - Interface: {interface}, {packet}", f"SWITCH->{interface}")
        else:
            self.log_event(f"Forward failed - Invalid interface: {interface}", "ERROR")

    def forward_to_switch(self, packet):
        dst_interface = 0
        if packet.dst in self.physical_map.values():
            for interface, mac in self.physical_map.items():
                if mac == packet.dst:
                    dst_interface = interface
                    break

        src_interface = 0
        if packet.dst in self.physical_map.values():
            for interface, mac in self.physical_map.items():
                if mac == packet.src:
                    src_interface = interface
                    break
        self.log_event(f"{packet} forwarded to switch", f"SWITCH@{dst_interface}")
        return src_interface, packet

    def log_packet(self, message):       
        with open(self.log_file, 'a') as f:
            f.write(f"{message}\n")
