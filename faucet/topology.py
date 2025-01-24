#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
import time
import os

class ThreeLayerTopo(Topo):
    # Your existing topology class remains the same
    "Three Layer Network Topology"

    def __init__(self):
        "Create three layer topo."

        # Initialize topology
        Topo.__init__(self)

        # Core Layer
        core = self.addSwitch('s1', dpid='0000000000000001')

        # Aggregation Layer
        agg1 = self.addSwitch('s2', dpid='0000000000000002')
        agg2 = self.addSwitch('s3', dpid='0000000000000003')

        # Access Layer
        access1 = self.addSwitch('s4', dpid='0000000000000004')
        access2 = self.addSwitch('s5', dpid='0000000000000005')

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
        # Hosts of switch 4
        hosts = []
        # Hosts of switch 4
        hosts.append(self.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('h2', ip='10.0.1.2/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('h3', ip='10.0.1.3/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.1.254'))
        # Hosts of switch 5
        hosts.append(self.addHost('h4', ip='10.0.2.1/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('h5', ip='10.0.2.2/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('h6', ip='10.0.2.3/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.2.254'))
        # Connect hosts to access switches
        self.addLink(hosts[0], access1) # h1 <-> s4-eth3
        self.addLink(hosts[1], access1) # h2 <-> s4-eth4
        self.addLink(hosts[2], access1) # h3 <-> s4-eth5
        self.addLink(hosts[3], access2) # h4 <-> s5-eth3
        self.addLink(hosts[4], access2) # h5 <-> s5-eth4
        self.addLink(hosts[5], access2) # h6 <-> s5-eth5


def run_tests():
    "Create network and run tests"
    topo = ThreeLayerTopo()
    
    # Create network with remote controller
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)
    net = Mininet(topo=topo, controller=c0)
    
    net.start()

    print("Waiting for network convergence...")
    time.sleep(10)

    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    # Run ping tests
    print("Running ping tests...")
    with open('results/ping_results.txt', 'w') as f:
        for h1 in net.hosts:
            for h2 in net.hosts:
                if h1 != h2:
                    ping_result = h1.cmd(f'ping -c 5 {h2.IP()}')
                    f.write(f"Ping from {h1.name} to {h2.name}:\n")
                    f.write(ping_result)
                    f.write('\n')

    # Run iperf tests
    print("Running iperf tests...")
    with open('results/iperf_results.txt', 'w') as f:
        # Start iperf servers on all hosts
        for host in net.hosts:
            host.cmd('iperf -s &')

        # Run iperf client tests
        for h1 in net.hosts:
            for h2 in net.hosts:
                if h1 != h2:
                    result = h1.cmd(f'iperf -c {h2.IP()} -t 5')
                    f.write(f"Iperf from {h1.name} to {h2.name}:\n")
                    f.write(result)
                    f.write('\n')

        # Kill iperf servers
        for host in net.hosts:
            host.cmd('killall iperf')

    # Collect flow statistics using OpenFlow protocol
    print("Collecting flow statistics...")
    total_packets = 0
    total_bytes = 0
    
    with open('results/flow_stats.txt', 'w') as f:
        for switch in net.switches:
            flows = switch.cmd('ovs-ofctl dump-flows ' + switch.name)
            f.write(f"Flows for switch {switch.name}:\n")
            f.write(flows)
            f.write('\n')
            
            # Sum up packets and bytes
            for flow in flows.split('\n'):
                if 'n_packets=' in flow:
                    try:
                        packets = int(flow.split('n_packets=')[1].split(',')[0])
                        bytes_count = int(flow.split('n_bytes=')[1].split(',')[0])
                        total_packets += packets
                        total_bytes += bytes_count
                    except:
                        continue

    print(f"\nTotal Statistics:")
    print(f"Total Packets: {total_packets}")
    print(f"Total Bytes: {total_bytes}")

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_tests()
