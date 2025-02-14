#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.node import OVSBridge
from time import sleep

class ThreeLayerTopo(Topo):
    "Three Layer Network Topology"

    def __init__(self):
        "Create three layer topo."

        # Initialize topology
        Topo.__init__(self)

        # Core Layer
        core1 = self.addSwitch('s1', dpid='0000000000000001', protocols='OpenFlow14')
        core2 = self.addSwitch('s2', dpid='0000000000000002', protocols='OpenFlow14')

        # Aggregation Layer
        agg11 = self.addSwitch('s11', dpid='0000000000000011', protocols='OpenFlow14')
        agg12 = self.addSwitch('s12', dpid='0000000000000012', protocols='OpenFlow14')
        agg13 = self.addSwitch('s13', dpid='0000000000000013', protocols='OpenFlow14')
        agg14 = self.addSwitch('s14', dpid='0000000000000014', protocols='OpenFlow14')

        # Access Layer
        access21 = self.addSwitch('s21', dpid='0000000000000021', protocols='OpenFlow14')
        access22 = self.addSwitch('s22', dpid='0000000000000022', protocols='OpenFlow14')
        access23 = self.addSwitch('s23', dpid='0000000000000023', protocols='OpenFlow14')
        access24 = self.addSwitch('s24', dpid='0000000000000024', protocols='OpenFlow14')
        access25 = self.addSwitch('s25', dpid='0000000000000025', protocols='OpenFlow14')
        access26 = self.addSwitch('s26', dpid='0000000000000026', protocols='OpenFlow14')
        access27 = self.addSwitch('s27', dpid='0000000000000027', protocols='OpenFlow14')
        access28 = self.addSwitch('s28', dpid='0000000000000028', protocols='OpenFlow14')

        # First establish all switch-to-switch connections
        self.addLink(core1, core2)  # s1-eth1 <-> s2-eth1
        
        # Core to Aggregation links
        self.addLink(core1, agg11)    # s1-eth2 <-> s11-eth1
        self.addLink(core1, agg12)    # s1-eth3 <-> s12-eth1
        self.addLink(core1, agg13)    # s1-eth4 <-> s13-eth1
        self.addLink(core1, agg14)    # s1-eth5 <-> s14-eth1

        self.addLink(core2, agg11)    # s2-eth2 <-> s11-eth2
        self.addLink(core2, agg12)    # s2-eth3 <-> s12-eth2
        self.addLink(core2, agg13)    # s2-eth4 <-> s13-eth2
        self.addLink(core2, agg14)    # s2-eth5 <-> s14-eth2

        # Aggregation redundancy link
        self.addLink(agg11, agg12)    # s11-eth3 <-> s12-eth3
        self.addLink(agg13, agg14)    # s13-eth3 <-> s14-eth3

        self.addLink(agg11, agg13)    # s11-eth4 <-> s13-eth4
        self.addLink(agg12, agg13)    # s12-eth4 <-> s13-eth5

        self.addLink(agg11, agg14)    # s11-eth5 <-> s14-eth4
        self.addLink(agg12, agg14)    # s12-eth5 <-> s14-eth5


        # Aggregation to Access links
        self.addLink(agg11, access21) # s11-eth6 <-> s21-eth1
        self.addLink(agg11, access22) # s11-eth7 <-> s22-eth1
        self.addLink(agg12, access23) # s12-eth6 <-> s23-eth1
        self.addLink(agg12, access24) # s12-eth7 <-> s24-eth1
        self.addLink(agg13, access25) # s13-eth6 <-> s25-eth1
        self.addLink(agg13, access26) # s13-eth7 <-> s26-eth1
        self.addLink(agg14, access27) # s14-eth6 <-> s27-eth1
        self.addLink(agg14, access28) # s14-eth7 <-> s28-eth1

        self.addLink(agg12, access21) # s12-eth8 <-> s21-eth2
        self.addLink(agg12, access22) # s12-eth9 <-> s22-eth2
        self.addLink(agg11, access23) # s11-eth8 <-> s23-eth2
        self.addLink(agg11, access24) # s11-eth9 <-> s24-eth2
        self.addLink(agg14, access25) # s14-eth8 <-> s25-eth2
        self.addLink(agg14, access26) # s14-eth9 <-> s26-eth2
        self.addLink(agg13, access27) # s13-eth8 <-> s27-eth2
        self.addLink(agg13, access28) # s13-eth9 <-> s28-eth2

        # Now add hosts and their connections
        hosts = []
        hosts.append(self.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('hx1', ip='10.0.1.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h2', ip='10.0.2.1/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('hx2', ip='10.0.2.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h3', ip='10.0.3.1/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.3.254'))
        hosts.append(self.addHost('hx3', ip='10.0.3.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h4', ip='10.0.4.1/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.4.254'))
        hosts.append(self.addHost('hx4', ip='10.0.4.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h5', ip='10.0.5.1/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.5.254'))
        hosts.append(self.addHost('hx5', ip='10.0.5.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h6', ip='10.0.6.1/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.6.254'))
        hosts.append(self.addHost('hx6', ip='10.0.6.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h7', ip='10.0.7.1/24', mac='00:00:00:00:00:07', defaultRoute='via 10.0.7.254'))
        hosts.append(self.addHost('hx7', ip='10.0.7.254/24', mac='00:00:00:00:00:ff'))
        hosts.append(self.addHost('h8', ip='10.0.8.1/24', mac='00:00:00:00:00:08', defaultRoute='via 10.0.8.254'))
        hosts.append(self.addHost('hx8', ip='10.0.8.254/24', mac='00:00:00:00:00:ff'))
        # Connect hosts to access switches
        self.addLink(hosts[0], access21) # h1 <-> s21-eth3
        self.addLink(hosts[1], access21) # hx1 <-> s21-eth4
        self.addLink(hosts[2], access22) # h2 <-> s22-eth3
        self.addLink(hosts[3], access22) # hx2 <-> s22-eth4
        self.addLink(hosts[4], access23) # h3 <-> s23-eth3
        self.addLink(hosts[5], access23) # hx3 <-> s23-eth4
        self.addLink(hosts[6], access24) # h4 <-> s24-eth3
        self.addLink(hosts[7], access24) # hx4 <-> s24-eth4
        self.addLink(hosts[8], access25) # h5 <-> s25-eth3
        self.addLink(hosts[9], access25) # hx5 <-> s25-eth4
        self.addLink(hosts[10], access26) # h6 <-> s26-eth3
        self.addLink(hosts[11], access26) # hx6 <-> s26-eth4
        self.addLink(hosts[12], access27) # h7 <-> s27-eth3
        self.addLink(hosts[13], access27) # hx7 <-> s27-eth4
        self.addLink(hosts[14], access28) # h8 <-> s28-eth3
        self.addLink(hosts[15], access28) # hx8 <-> s28-eth4

        # Add host internet
        internet = self.addHost('hi', ip='1.1.1.1/30', mac='00:00:00:00:00:ff', defaultRoute='via 1.1.1.2')
        s = self.addSwitch('s100', dpid='0000000000000100', protocols='OpenFlow14')  # regular L2 switch acting as relay for internet
        self.addLink(core1, s)  # s1-eth6 <-> hi (internet)
        self.addLink(core2, s)  # s2-eth6 <-> hi (internet)
        self.addLink(s, internet) 
        self.addLink(s, self.addHost('hx9', ip='1.1.1.2/30', mac='00:00:00:00:00:ff')) # (internet's gateway)

# topos = { 'threelayer': ( lambda: ThreeLayerTopo() ) }
net = Mininet(topo=ThreeLayerTopo(), controller=RemoteController)
net.start()

# to collect packets
"""net.get('h1').cmd("tcpdump -i h1-eth0 -w h1-eth0.pcap &")
net.get('h2').cmd("tcpdump -i h2-eth0 -w h2-eth0.pcap &")
net.get('h3').cmd("tcpdump -i h3-eth0 -w h3-eth0.pcap &")
net.get('h4').cmd("tcpdump -i h4-eth0 -w h4-eth0.pcap &")
net.get('h5').cmd("tcpdump -i h5-eth0 -w h5-eth0.pcap &")
net.get('h6').cmd("tcpdump -i h6-eth0 -w h6-eth0.pcap &")
net.get('hi').cmd("tcpdump -i hi-eth0 -w hi-eth0.pcap &")

net.get('s1').cmd("tcpdump -i s1-eth1 -w s1-eth1.pcap &")
net.get('s1').cmd("tcpdump -i s1-eth2 -w s1-eth2.pcap &")

net.get('s2').cmd("tcpdump -i s2-eth2 -w s2-eth2.pcap &")

net.get('s2').cmd("tcpdump -i s2-eth3 -w s2-eth3.pcap &")
net.get('s2').cmd("tcpdump -i s2-eth4 -w s2-eth4.pcap &")
net.get('s3').cmd("tcpdump -i s3-eth3 -w s3-eth3.pcap &")
net.get('s3').cmd("tcpdump -i s3-eth4 -w s3-eth4.pcap &")"""

# to perform iperf
"""net.get('hi1').cmd("iperf -s -u &")
net.get('h2').cmd("iperf -s &")
net.get('h5').cmd("iperf -s &")
sleep(3)

net.get('h1').cmd("iperf -c -u 1.1.1.1 -t 30 &")
net.get('h4').cmd("iperf -c -u 1.1.1.1 -t 30 &")
net.get('h3').cmd("iperf -c 10.0.2.5 -t 30 &")
net.get('h6').cmd("iperf -c 10.0.1.2 -t 30 &")

# perform ping
net.get('h1').cmd("ping h2 &")
net.get('h4').cmd("ping h5 &")
net.get('h3').cmd("ping h6 &")
net.get('h1').cmd("ping hi &")
net.get('h4').cmd("ping hi &")"""

CLI(net)  # Open the Mininet CLI
net.stop()  # Stop the network when done
