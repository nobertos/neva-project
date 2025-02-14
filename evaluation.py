#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.topo import Topo
from time import sleep
import subprocess
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np

class ThreeLayerTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        
        core = self.addSwitch('s1', dpid='0000000000000001')
        
        agg1 = self.addSwitch('s2', dpid='0000000000000002')
        agg2 = self.addSwitch('s3', dpid='0000000000000003')
        
        access1 = self.addSwitch('s4', dpid='0000000000000004')
        access2 = self.addSwitch('s5', dpid='0000000000000005')
        
        self.addLink(core, agg1)    
        self.addLink(core, agg2)    
        
        self.addLink(agg1, agg2)    
        
        self.addLink(agg1, access1) 
        self.addLink(agg2, access1) 
        self.addLink(agg1, access2) 
        self.addLink(agg2, access2) 
        
        hosts = []
        hosts.append(self.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('h2', ip='10.0.1.2/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.1.254'))
        hosts.append(self.addHost('h3', ip='10.0.1.3/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.1.254'))
        
        hosts.append(self.addHost('h4', ip='10.0.2.1/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('h5', ip='10.0.2.2/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.2.254'))
        hosts.append(self.addHost('h6', ip='10.0.2.3/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.2.254'))
        
        self.addLink(hosts[0], access1)
        self.addLink(hosts[1], access1)
        self.addLink(hosts[2], access1)
        self.addLink(hosts[3], access2)
        self.addLink(hosts[4], access2)
        self.addLink(hosts[5], access2)

def analyze_pcap(file_path):
    try:
        subprocess.check_call(["tshark", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("tshark is not installed. Please install it using 'sudo apt-get install tshark'.")
        return 0, 0

    try:
        packet_count = int(subprocess.check_output(
            f"tshark -r {file_path} -T fields -e frame.number | wc -l", shell=True
        ))
        total_size = int(subprocess.check_output(
            f"tshark -r {file_path} -T fields -e frame.len | awk '{{sum+=$1}} END {{print sum}}'", shell=True
        ))
        return packet_count, total_size
    except (subprocess.CalledProcessError, ValueError):
        print(f"Error analyzing {file_path}")
        return 0, 0

def plot_packet_statistics(useful_packets, useless_packets):
    plt.figure(figsize=(12, 6))
    
    packet_types = ['Useful Packets', 'Useless Packets']
    packet_counts = [useful_packets['count'], useless_packets['count']]
    packet_sizes = [useful_packets['size'], useless_packets['size']]
    
    plt.subplot(1, 2, 1)
    plt.bar(packet_types, packet_counts, color=['green', 'red'])
    plt.title('Packet Count Comparison')
    plt.ylabel('Number of Packets')
    for i, count in enumerate(packet_counts):
        plt.text(i, count, str(count), ha='center', va='bottom')
    
    plt.subplot(1, 2, 2)
    plt.bar(packet_types, packet_sizes, color=['green', 'red'])
    plt.title('Packet Size Comparison')
    plt.ylabel('Total Size (bytes)')
    for i, size in enumerate(packet_sizes):
        plt.text(i, size, str(size), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('output_graphs.png')
    plt.close()

def calculate_statistics():
    useful_packets = {'count': 0, 'size': 0}
    useless_packets = {'count': 0, 'size': 0}

    for i in range(1, 7):
        file_path = f"h{i}.pcap"
        packet_count, total_size = analyze_pcap(file_path)
        if i <= 3:
            useful_packets['count'] += packet_count
            useful_packets['size'] += total_size
        else:
            useful_packets['count'] += packet_count
            useful_packets['size'] += total_size

    for sw in ['s1', 's2', 's3']:
        for eth in range(1, 5):
            file_path = f"{sw}-eth{eth}.pcap"
            packet_count, total_size = analyze_pcap(file_path)
            useless_packets['count'] += packet_count
            useless_packets['size'] += total_size

    total_packets = useful_packets['count'] + useless_packets['count']
    total_size = useful_packets['size'] + useless_packets['size']

    if total_packets == 0 or total_size == 0:
        print("No packets found in capture files.")
        return

    print("\nNetwork Traffic Analysis:")
    print(f"Useful Packets: {useful_packets['count']} ({round(useful_packets['count']/total_packets * 100, 2)}%)")
    print(f"Useful Packets Size: {useful_packets['size']} bytes ({round(useful_packets['size']/total_size * 100, 2)}%)")
    print(f"Useless Packets: {useless_packets['count']} ({round(useless_packets['count']/total_packets * 100, 2)}%)")
    print(f"Useless Packets Size: {useless_packets['size']} bytes ({round(useless_packets['size']/total_size * 100, 2)}%)")

    plot_packet_statistics(useful_packets, useless_packets)
    print("\nGraphs have been saved to 'output_graphs.png'")

def start_network():
    topo = ThreeLayerTopo()
    net = Mininet(topo=topo, controller=None, switch=OVSSwitch)
    
    net.addController('c0', controller=RemoteController, ip="127.0.0.1", port=6653)
    
    print("\nStarting Network...")
    net.start()
    
    print("\nWaiting 20 seconds for network convergence...")
    sleep(20)
    
    print("\nStarting Network Monitoring...")
    
    for i in range(1, 7):
        host = f'h{i}'
        print(f"Starting tcpdump on {host}")
        net.get(host).cmd(f"tcpdump -i {host}-eth0 -w {host}.pcap &")

    for sw in ['s1', 's2', 's3']:
        for eth in range(1, 5):
            print(f"Starting tcpdump on {sw}-eth{eth}")
            net.get(sw).cmd(f"tcpdump -i {sw}-eth{eth} -w {sw}-eth{eth}.pcap &")

    print("\nStarting Performance Tests...")
    
    print("Starting iperf servers on h2 and h5...")
    net.get('h2').cmd("iperf -s &")
    net.get('h5').cmd("iperf -s &")
    sleep(2)

    print("Running iperf tests...")
    net.get('h1').cmd("iperf -c 10.0.1.2 -t 20 &")
    net.get('h4').cmd("iperf -c 10.0.2.2 -t 20 &")
    net.get('h3').cmd("iperf -c 10.0.2.2 -t 20 &")
    net.get('h6').cmd("iperf -c 10.0.1.2 -t 20 &")

    print("Running ping tests...")
    net.get('h1').cmd("ping -c 10 10.0.1.2 > ping_intra_subnet1.txt &")
    net.get('h4').cmd("ping -c 10 10.0.2.2 > ping_intra_subnet2.txt &")
    net.get('h3').cmd("ping -c 10 10.0.2.1 > ping_inter_subnet1.txt &")
    net.get('h6').cmd("ping -c 10 10.0.1.1 > ping_inter_subnet2.txt &")

    print("\nWaiting for tests to complete...")
    sleep(25)

    print("\nAnalyzing network traffic...")
    calculate_statistics()

    print("\nNetwork is ready for interaction.")
    CLI(net)
    
    print("\nStopping Network...")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    start_network()
