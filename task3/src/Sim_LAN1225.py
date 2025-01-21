from re import match
from lib_final import SwitchFabric, Packet
from queue import Queue

class Host:
    def __init__(self, mac, interface, vlan_id=1, ip_address="0.0.0.0"):
        if not match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac):
            raise ValueError("Invalid MAC address format")
        self.mac = mac
        self.interface = interface
        self.vlan_id = vlan_id
        self.ip_address = ip_address
        self.buffer = []

    def send_packet(self, dst_mac, payload, switch, dst_ip):
        packet = Packet(
            src=self.mac,
            dst=dst_mac,
            src_ip=self.ip_address,
            dst_ip=dst_ip,
            payload=payload,
            vlan_id=self.vlan_id
        )
        switch.handle_packet(packet, self.interface)  

    def receive_packet(self, packet):
        if (packet.dst == self.mac or packet.dst == "FF:FF:FF:FF:FF:FF") and packet.vlan_id == self.vlan_id:
            self.buffer.append(packet)

class Router:
    def __init__(self):
        self.interfaces = {}
        self.route_table = {}

    def add_interface(self, vlan_id, interface):
        self.interfaces[vlan_id] = interface

    def add_route(self, destination, next_hop=None, interface=None):
        self.route_table[destination] = (next_hop, interface)

    def route_packet(self, packet, src_vlan_id):
        destination = packet.dst_ip
        if destination in self.route_table:
            next_hop, out_interface = self.route_table[destination]
            if out_interface:
                packet.vlan_id = out_interface.vlan_id
                out_interface.receive_packet(packet)
            else:
                print(f"Packet destination {destination} sent to next hop {next_hop}")
        else:
            print("No route to the destination")

class SwitchFabric:
    def __init__(self):
        self.queue = Queue()
        self.physical_map = {}
        self.interfaces = {}
        self.vlan_map = {}
        self.log_file = "fabric_log.txt"
        with open(self.log_file, 'w') as f:
            f.write("Switch Fabric Log Start\n")
        self.log_event("Switch Fabric initialized")

    def log_event(self, message, category="INFO"):
        with open(self.log_file, 'a') as f:
            f.write(f"[{category}] {message}\n")

    def forward_to_interface(self, packet, interface):
        host = self.interfaces.get(interface)
        if host:
            host.receive_packet(packet)
            self.log_event(f"Packet forwarded to interface {interface}", "FORWARD")
        else:
            self.log_event(f"Interface {interface} not found, unable to forward", "ERROR")

class Switch:
    def __init__(self, fabric, num_interfaces=8):
        self.num_interfaces = num_interfaces
        self.interfaces = {i: None for i in range(self.num_interfaces)}
        self.mac_table = {}
        self.vlan_table = {}
        self.fabric = fabric
        self.router = Router()

    def handle_packet(self, packet, input_interface):
        # Learn the source MAC address and corresponding interface and VLAN
        if packet.src not in self.mac_table:
            self.mac_table[packet.src] = input_interface
            self.vlan_table[packet.src] = packet.vlan_id
            self.fabric.log_event(f"Learned MAC {packet.src} on interface {input_interface} and VLAN {packet.vlan_id}")

        # Check if the destination MAC address is known
        if packet.dst in self.mac_table:
            dst_interface = self.mac_table[packet.dst]
            dst_vlan = self.vlan_table.get(packet.dst)

            if dst_vlan == packet.vlan_id:
                # VLAN communication, forward directly
                self.fabric.forward_to_interface(packet, dst_interface)
                print(f"packet = {packet}, interface = {dst_interface}")
                self.fabric.log_event(f"VLAN forwarding: {packet.src} -> {packet.dst} in VLAN {packet.vlan_id}")
            else:
                # Inter-VLAN communication, forward to router
                self.fabric.log_event(f"Inter-VLAN forwarding: {packet.src} (VLAN {packet.vlan_id}) -> {packet.dst} (VLAN {dst_vlan})")
                self.router.route_packet(packet, packet.vlan_id)
        else:
            if packet.dst == "FF:FF:FF:FF:FF:FF":
                # Broadcast packet, flood within the same VLAN
                self.fabric.log_event(f"Broadcast packet flooding in VLAN {packet.vlan_id}")
                self.flood_packet(packet, input_interface)
            else:
                pass

    def get_interface_by_mac(self, mac):
        return self.mac_table.get(mac)

    def update_mac_table(self, host):
        # Remove the old MAC address
        for mac, iface in list(self.mac_table.items()):
            if iface == host.interface:
                del self.mac_table[mac]
                del self.vlan_table[mac]

        # Add the new MAC address
        self.mac_table[host.mac] = host.interface
        self.vlan_table[host.mac] = host.vlan_id
        self.fabric.log_event(f"Updated MAC table: {host.mac} on interface {host.interface} and VLAN {host.vlan_id}")

    def flood_packet(self, packet, input_interface):
        for interface, host in self.interfaces.items():
            if host and host.vlan_id == packet.vlan_id and interface != input_interface:
                flooded_packet = Packet(
                    src=packet.src,
                    dst=host.mac,
                    src_ip=packet.src_ip,
                    dst_ip=host.ip_address,
                    payload=packet.payload,
                    vlan_id=packet.vlan_id
                )
                self.fabric.forward_to_interface(flooded_packet, interface)
                
                self.fabric.log_event(f"Flooded packet within VLAN {packet.vlan_id} to interface {interface}")

class FixedSwitchFabric(SwitchFabric):
    def connect_host_to_switch(self, host, switch):
        switch.interfaces[host.interface] = host
        switch.mac_table[host.mac] = host.interface
        switch.vlan_table[host.mac] = host.vlan_id
        self.interfaces[host.interface] = host
        self.log_event(f"Host {host.mac} connected to switch interface {host.interface} in VLAN {host.vlan_id}")
