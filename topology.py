#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from time import sleep

class ThreeLayerTopo(Topo):
    "Three Layer Network Topology"

    def __init__(self):
        "Create three layer topo."

        # Initialize topology
        Topo.__init__(self)

        # Core Layer
        core = self.addSwitch('s1', dpid='0000000000000001', protocols='OpenFlow14')

        # Aggregation Layer
        agg1 = self.addSwitch('s2', dpid='0000000000000002', protocols='OpenFlow14')
        agg2 = self.addSwitch('s3', dpid='0000000000000003', protocols='OpenFlow14')

        # Access Layer
        access1 = self.addSwitch('s4', dpid='0000000000000004', protocols='OpenFlow14')
        access2 = self.addSwitch('s5', dpid='0000000000000005', protocols='OpenFlow14')

        # First establish all switch-to-switch connections
        
        # Core to Aggregation links
        self.addLink(core, agg1)    # s1-eth1 <-> s2-eth1
        self.addLink(core, agg2)    # s1-eth2 <-> s3-eth1

        # Aggregation redundancy link
        self.addLink(agg1, agg2)    # s2-eth2 <-> s3-eth2

        # Aggregation to Access links
        self.addLink(agg1, access1) # s2-eth3 <-> s4-eth1
        self.addLink(agg2, access1) # s3-eth3 <-> s4-eth2
        self.addLink(agg1, access2) # s2-eth4 <-> s5-eth1
        self.addLink(agg2, access2) # s3-eth4 <-> s5-eth2

        # Now add hosts and their connections
        hosts = []
        # Hosts of switch 4
        hosts.append(self.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('h2', ip='10.0.1.2/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('h3', ip='10.0.1.3/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('hx1', ip='10.0.1.254/24', mac='00:00:00:00:00:ff'))
        # Hosts of switch 5
        hosts.append(self.addHost('h4', ip='10.0.2.4/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('h5', ip='10.0.2.5/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('h6', ip='10.0.2.6/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('hx2', ip='10.0.2.254/24', mac='00:00:00:00:00:ff'))
        # Connect hosts to access switches
        self.addLink(hosts[0], access1) # h1 <-> s4-eth3
        self.addLink(hosts[1], access1) # h2 <-> s4-eth4
        self.addLink(hosts[2], access1) # h3 <-> s4-eth5
        self.addLink(hosts[3], access1) # hx1 <-> s4-eth6
        self.addLink(hosts[4], access2) # h4 <-> s5-eth3
        self.addLink(hosts[5], access2) # h5 <-> s5-eth4
        self.addLink(hosts[6], access2) # h6 <-> s5-eth5
        self.addLink(hosts[7], access2) # hx2 <-> s4-eth6

        # Add host internet
        internet = self.addHost('hi', ip='1.1.1.1/30', mac='00:00:00:00:00:ff', defaultRoute='via 1.1.1.2')
        self.addLink(internet, core) # s1-eth3 <-> hi (internet)
        self.addLink(core, self.addHost('hx3', ip='1.1.1.2/30', mac='00:00:00:00:00:ff')) # s1-eth4 <-> hx3 (internet's gateway)

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
net.get('hi').cmd("iperf -s -u &")
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
net.get('h4').cmd("ping hi &")

CLI(net)  # Open the Mininet CLI
net.stop()  # Stop the network when done
