from Sim_LAN1225 import Host, Switch, Router, FixedSwitchFabric, Packet
from lib_final import SwitchFabric

def test_vlan_and_routing_functionality():
    fabric = FixedSwitchFabric()
    router = Router()
    switch = Switch(fabric)

    # VLAN 10 Hosts
    host1 = Host("00:00:00:00:00:01", 0, vlan_id=10)
    host1.ip_address = "192.168.10.1"
    host3 = Host("00:00:00:00:00:03", 2, vlan_id=10)
    host3.ip_address = "192.168.10.3"

    # VLAN 20 Hosts
    host2 = Host("00:00:00:00:00:02", 1, vlan_id=20)
    host2.ip_address = "192.168.20.2"
    host4 = Host("00:00:00:00:00:04", 3, vlan_id=20)
    host4.ip_address = "192.168.20.4"

    # Connecting hosts to switch
    fabric.connect_host_to_switch(host1, switch)
    fabric.connect_host_to_switch(host2, switch)
    fabric.connect_host_to_switch(host3, switch)
    fabric.connect_host_to_switch(host4, switch)

    # Router Configuration
    switch.router = router
    router.add_interface(10, switch.interfaces[0])  # Interface 0 connects to VLAN 10
    router.add_interface(20, switch.interfaces[1])  # Interface 1 connects to VLAN 20
    # Adding route entries
    router.add_route("192.168.10.3", None, interface=switch.interfaces[2])  # Inside VLAN 10
    router.add_route("192.168.20.2", None, interface=switch.interfaces[1])  # Inside VLAN 20

    # Test 1: Intra-VLAN Communication (VLAN 10)
    print("\nTest 1: Intra-VLAN Communication (VLAN 10)...")
    try:
        host1.send_packet(host3.mac, "Hello", switch, host3.ip_address)
        assert len(host3.buffer) > 0, "Intra-VLAN communication failed to receive packet"
        print("\u2713 Intra-VLAN Communication Test Passed")
    except AssertionError as e:
        print(f"\u2717 Intra-VLAN Communication Test Failed: {str(e)}")

    # Test 2: Inter-VLAN Communication (VLAN 10 to VLAN 20)
    print("\nTest 2: Inter-VLAN Communication (VLAN 10 to VLAN 20)...")
    try:
        host1.send_packet(host2.mac, "Hello, host2", switch, host2.ip_address)
        assert len(host2.buffer) > 0, "Inter-VLAN communication failed to receive packet"
        print("\u2713 Inter-VLAN Communication Test Passed")
    except AssertionError as e:
        print(f"\u2717 Inter-VLAN Communication Test Failed: {str(e)}")

    # Test 3: VLAN Flooding and Isolation
    # Clear host buffers
    host1.buffer = []
    host2.buffer = []
    host3.buffer = []
    host4.buffer = []
    print("\nTest 3: VLAN Flooding and Isolation...")
    try:
        # Send broadcast packet inside VLAN 10
        broadcast_packet = Packet(
            src=host1.mac,
            dst="FF:FF:FF:FF:FF:FF",
            src_ip=host1.ip_address,
            dst_ip="255.255.255.255",
            payload="Broadcast Message",
            vlan_id=10
        )
        switch.handle_packet(broadcast_packet, host1.interface)

        # Check that only hosts in VLAN 10 receive the broadcast
        assert len(host1.buffer) == 0, "Host 1 should not receive its own broadcast"
        assert len(host3.buffer) > 0, "Host 3 should receive the broadcast"
        assert len(host2.buffer) == 0, "Host 2 (VLAN 20) should not receive the broadcast"
        assert len(host4.buffer) == 0, "Host 4 (VLAN 20) should not receive the broadcast"
        print("\u2713 VLAN Flooding and Isolation Test Passed")
    except AssertionError as e:
        print(f"\u2717 VLAN Flooding and Isolation Test Failed: {str(e)}")

    return

# Fixed Host Connection Method
class FixedSwitchFabric(SwitchFabric):
    def connect_host_to_switch(self, host, switch):
        switch.interfaces[host.interface] = host
        switch.mac_table[host.mac] = host.interface
        switch.vlan_table[host.mac] = host.vlan_id
        self.interfaces[host.interface] = host
        self.log_event(f"Host {host.mac} connected to switch interface {host.interface} in VLAN {host.vlan_id}")

# Test MAC Table Update
def test_mac_table_update():
    fabric = FixedSwitchFabric()
    switch = Switch(fabric)

    # VLAN 10 Hosts
    host1 = Host("00:00:00:00:00:01", 0, vlan_id=10)
    host1.ip_address = "192.168.10.1"
    host3 = Host("00:00:00:00:00:03", 2, vlan_id=10)
    host3.ip_address = "192.168.10.3"

    # VLAN 20 Hosts
    host2 = Host("00:00:00:00:00:02", 1, vlan_id=20)
    host2.ip_address = "192.168.20.2"
    host4 = Host("00:00:00:00:00:04", 3, vlan_id=20)
    host4.ip_address = "192.168.20.4"

    # Connecting hosts to switch
    fabric.connect_host_to_switch(host1, switch)
    fabric.connect_host_to_switch(host2, switch)
    fabric.connect_host_to_switch(host3, switch)
    fabric.connect_host_to_switch(host4, switch)


    # Print old host table
    print("Old Host Table:")
    for mac, interface in switch.mac_table.items():
        print(f"MAC: {mac}, Interface: {interface}")
    
    # Update host1's MAC and interface
    host1.mac = "00:00:00:00:00:FF"
    host1.interface = 2
    switch.update_mac_table(host1)
    print("\nUpdated Host Table:")
    for mac, interface in switch.mac_table.items():
        print(f"MAC: {mac}, Interface: {interface}")
    assert switch.mac_table.get("00:00:00:00:00:FF") == 2, "MAC Table update failed"
    print("\u2713 MAC Table Update Test Passed")

if __name__ == "__main__":
    print("Running VLAN and Routing Tests:")
    test_vlan_and_routing_functionality()

    print("\nRunning MAC Table Update Test:")
    test_mac_table_update()
