# Data Communications and Networking Final Project: Sim-LAN

## Abstract

The experiment comprehensively demonstrated the implementation and functionality of network communication topologies and advanced features, including Bus topology, Star topology with a switch, and VLAN-based routing. Each task contributed to validating critical functionalities such as packet forwarding, MAC address learning, VLAN isolation, and routing.

## Task 1: Bus Implementation



#### **Description**

A bus topology was implemented where multiple hosts are connected to a shared communication medium (the Bus). Each host can send packets to others through the Bus. The main components include:

- **Host Class:** Represents network hosts with unique MAC addresses.
- **Bus Class:** Facilitates packet broadcasting and handles connected hosts.

#### **Key Features**

1. **Broadcasting Packets:** Packets are broadcast to all connected hosts except the sender.
2. **Selective Reception:** Hosts filter and store only the packets addressed to their MAC.

#### Key Functions

**send packet**

```python
    def send_packet(self, dst_mac, payload, bus):
        """
        Send a packet to the bus.
        Parameters:
        - dst_mac: Destination MAC address
        - payload: Packet content
        - bus: Bus object
        """
        # Create a packet object
        packet = Packet(src=self.mac, dst=dst_mac, payload=payload)
        # Call the bus's broadcast function to send the packet
        bus.broadcast(packet)
```

**receive packet**

```python
    def receive_packet(self, packet):
        """
        Receive and process a packet sent from the bus.
        Parameters:
        - packet: Received packet object
        """
        # Check if the packet's destination address matches the host's MAC address
        if packet.dst == self.mac:
            # If it matches, store the packet in the buffer
            self.buffer.append(packet)
```

#### **Testing and Results**

Tests were conducted using `test_bus.py` to validate the functionality:

1. **Broadcast Packet Test:** Verified that packets are broadcast to all hosts except the sender and received correctly by the intended recipient.
2. **Discard Unaddressed Packet Test:** Ensured that unaddressed hosts do not receive packets.


## Task 2: Star Implementation


#### **Description**

A Star topology was implemented using a central Switch that connects all hosts. The Switch performs MAC address learning and selective forwarding of packets. The main components include:

- **Host Class:** Represents network hosts with MAC addresses and interfaces.

- **Switch Class:** Implements a forwarding mechanism and maintains a MAC address table.

- **Switch Fabric:** Connects hosts to the Switch and manages physical interfaces.

#### **Key Features**

1. **Flooding:** The Switch floods packets if the destination MAC is unknown.
2. **MAC Learning:** The Switch learns the source MAC address and its associated interface for future forwarding.
3. **Selective Forwarding:** Packets are forwarded only to the specific interface of the destination host.

#### Key functions

**send packet**

```python
    def send_packet(self, dst_mac, payload, switch):
        """
        Send a packet to the switch.
        Parameters:
        - dst_mac: Destination MAC address
        - payload: Packet content
        - switch: Switch object
        """
        packet = Packet(src=self.mac, dst=dst_mac, payload=payload)  # Create a packet
        switch.handle_packet(packet)  # Pass the packet to the switch for processing

```

**receive packet**

```python
    def receive_packet(self, packet):
        """
        Receive and process a packet forwarded from the switch.
        Parameters:
        - packet: Packet object
        """
        if packet.dst == self.mac:  # If the destination MAC address matches this host
            self.buffer.append(packet)  # Store the packet in the buffer
```

**Switch**

```python
class Switch:
    def __init__(self, fabric, num_interfaces=8):
        self.num_interfaces = num_interfaces
        self.interfaces = {}
        self.mac_table = {}
        self.fabric = fabric
        for i in range(self.num_interfaces):
            self.interfaces[i] = None

    def handle_packet(self, packet):
        """
        Process a packet.
        Parameters:
        - packet: Packet object
        """
        # Learn the source MAC address
        if packet.src not in self.mac_table:
            self.mac_table[packet.src] = self.get_interface_by_mac(packet.src)

        # Look up the interface for the destination MAC address
        dst_interface = self.mac_table.get(packet.dst)
        if dst_interface is not None:  # If the destination interface is found, forward directly
            self.fabric.forward_to_interface(packet, dst_interface) 
        else:  # If the destination interface is unknown, flood the packet
            for interface, host in self.interfaces.items():
                if host and host.interface != self.get_interface_by_mac(packet.src):
                    self.fabric.forward_to_interface(packet, interface)

    def get_interface_by_mac(self, mac):
        """
        Get the interface number by MAC address.
        Parameters:
        - mac: MAC address
        Returns:
        - Interface number
        """
        for interface, host in self.interfaces.items():
            if host and host.mac == mac:
                return interface
        return None
```

#### **Testing and Results**

Tests were conducted using `test_switch.py` to validate the functionality:

1. **Initial Flooding Test:** Ensured that packets were flooded to all interfaces when the destination MAC was unknown.
2. **MAC Learning Test:** Verified that the Switch learned source MAC addresses and associated interfaces correctly.
3. **Selective Forwarding Test:** Ensured that packets were forwarded only to the correct interface.

**Results:**


## Task 3: VLAN, Router, Switch table update

Task 3 implements and tests a simulated Local Area Network (LAN) with VLANs, routing functionality, and MAC table updates. This task aims to verify key functionalities such as intra-VLAN communication, inter-VLAN routing, VLAN isolation, and the dynamic update of the MAC table.

#### **Task Description**

1. **VLAN Implementation:** Virtual LAN (VLAN) was introduced to segment network traffic logically.
2. **Routing Between VLANs:** A router was implemented to enable communication across different VLANs.
3. **MAC Table Updates:** The switch dynamically learns and updates MAC addresses and interface mappings.
4. **Switch Table Update Mechanism:** Hosts are connected to the switch with VLAN mappings, and the switch dynamically handles MAC-to-interface updates.

#### **Components**

1. **Host**

- Hosts have MAC addresses, IP addresses, VLAN IDs, and interfaces.
- Can send packets to a destination MAC address within the same or different VLAN.

2. **Switch**

- Maintains a MAC table, VLAN table, and interfaces.
- Handles intra-VLAN communication via direct forwarding.
- Routes packets for inter-VLAN communication via a connected router.
- Supports VLAN isolation and broadcasts within a VLAN.

3. **Router**

- Adds interfaces for VLANs.
- Maintains a routing table to determine the next hop or outgoing interface for inter-VLAN communication.

4. **Switch Fabric**

- Connects hosts to the switch and enables packet forwarding.

#### Key functions

**send and receive packet**

```python
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
```

**router**

```python
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
```

**update switch table**

```python
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
```

**flooding with VLAN isolation**

```python
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
```

### Tests

#### **Test 1: Intra-VLAN Communication**

- **Setup:** Hosts `Host1` and `Host3` are configured in VLAN 10.
- **Objective:** Verify that packets are delivered between hosts in the same VLAN.
- **Result:** Packets were successfully delivered, confirming correct intra-VLAN communication.

#### **Test 2: Inter-VLAN Communication**

- **Setup:** `Host1` (VLAN 10) sends a packet to `Host2` (VLAN 20) via the router.
- **Objective:** Ensure packets are routed correctly between VLANs.
- **Result:** Packets were routed and received by the destination host, validating inter-VLAN communication.

#### **Test 3: VLAN Flooding and Isolation**

- **Setup:** A broadcast packet is sent from `Host1` (VLAN 10).
- **Objective:** Verify that only hosts in the same VLAN (VLAN 10) receive the broadcast.
- **Result:** The broadcast was received only by `Host3` (in VLAN 10), confirming VLAN isolation.

#### **Test 4: MAC Table Update**

- **Setup:** `Host1` changes its MAC address and interface. The switch updates its MAC table.
- **Objective:** Ensure the switch dynamically updates the MAC-to-interface mapping.
- **Result:** The switch successfully updated the MAC table to reflect the changes.

#### Result


## Conclusion

The experiment successfully simulated real-world networking scenarios, demonstrating the evolution from basic shared communication (Bus topology) to more complex, scalable, and efficient designs (Star topology and VLANs). The tasks highlighted the importance of modular network components, such as switches and routers, in building reliable and high-performing networks.
