#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
import matplotlib
matplotlib.use('Agg')  # This line must come before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import time
import subprocess
import re

class ThreeLayerTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        # Core Layer
        core = self.addSwitch('s1', dpid='0000000000000001')
        # Aggregation Layer
        agg1 = self.addSwitch('s2', dpid='0000000000000002')
        agg2 = self.addSwitch('s3', dpid='0000000000000003')
        # Access Layer
        access1 = self.addSwitch('s4', dpid='0000000000000004')
        access2 = self.addSwitch('s5', dpid='0000000000000005')

        # Core to Aggregation links
        self.addLink(core, agg1)
        self.addLink(core, agg2)
        self.addLink(agg1, agg2)
        self.addLink(agg1, access1)
        self.addLink(agg2, access1)
        self.addLink(agg1, access2)
        self.addLink(agg2, access2)

        # Add hosts
        hosts = []
        for i in range(1, 4):
            hosts.append(self.addHost(f'h{i}',
                                   ip=f'10.0.1.{i}/24',
                                   mac=f'00:00:00:00:00:0{i}',
                                   defaultRoute='via 10.0.1.254'))

        for i in range(4, 7):
            hosts.append(self.addHost(f'h{i}',
                                   ip=f'10.0.2.{i-3}/24',
                                   mac=f'00:00:00:00:00:0{i}',
                                   defaultRoute='via 10.0.2.254'))

        # Connect hosts to switches
        for i in range(3):
            self.addLink(hosts[i], access1)
        for i in range(3, 6):
            self.addLink(hosts[i], access2)

def collect_stats(switch):
    """Collect OpenFlow statistics from a switch"""
    try:
        # Get flow stats
        flow_cmd = f"ovs-ofctl dump-flows {switch}"
        flow_output = subprocess.check_output(flow_cmd.split(), universal_newlines=True)

        # Get port stats to capture control plane traffic
        port_cmd = f"ovs-ofctl dump-ports {switch}"
        port_output = subprocess.check_output(port_cmd.split(), universal_newlines=True)

        # Parse control plane packets
        control_packets = 0

        # Count packets sent to controller (table-miss)
        for line in flow_output.split('\n'):
            if 'actions=CONTROLLER' in line and 'n_packets' in line:
                match = re.search(r'n_packets=(\d+)', line)
                if match:
                    control_packets += int(match.group(1))

        # Count packets from controller port
        for line in port_output.split('\n'):
            if 'LOCAL' in line:
                rx_match = re.search(r'rx pkts=(\d+)', line)
                tx_match = re.search(r'tx pkts=(\d+)', line)
                if rx_match:
                    control_packets += int(rx_match.group(1))
                if tx_match:
                    control_packets += int(tx_match.group(1))

        # Parse data plane packets (all other flows)
        data_packets = 0
        for line in flow_output.split('\n'):
            if 'n_packets' in line and 'actions=CONTROLLER' not in line:
                match = re.search(r'n_packets=(\d+)', line)
                if match:
                    data_packets += int(match.group(1))

        return control_packets, data_packets
    except Exception as e:
        print(f"Error collecting stats from {switch}: {str(e)}")
        return 0, 0

def plot_stats(stats_data):
    """Create visualization of network statistics"""
    # Calculate total packets sent for each data point
    total_packets = [x[1] + x[2] for x in stats_data]  # control + data packets
    control = [x[1] for x in stats_data]
    data = [x[2] for x in stats_data]

    plt.figure(figsize=(12, 6))

    # Create subplot for control plane
    plt.subplot(1, 2, 1)
    plt.scatter(total_packets, control, c='red', alpha=0.6)
    plt.plot(np.unique(total_packets),
            np.poly1d(np.polyfit(total_packets, control, 1))(np.unique(total_packets)),
            'r--', alpha=0.8)
    plt.title('Control Plane Traffic Analysis')
    plt.xlabel('Total Packets Sent')
    plt.ylabel('Control Plane Packets')
    plt.grid(True)

    # Create subplot for data plane
    plt.subplot(1, 2, 2)
    plt.scatter(total_packets, data, c='blue', alpha=0.6)
    plt.plot(np.unique(total_packets),
            np.poly1d(np.polyfit(total_packets, data, 1))(np.unique(total_packets)),
            'b--', alpha=0.8)
    plt.title('Data Plane Traffic Analysis')
    plt.xlabel('Total Packets Sent')
    plt.ylabel('Data Plane Packets')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('traffic_analysis.png')
    plt.close()

def run_network():
    """Run the network and collect statistics"""
    setLogLevel('info')

    # Create network with remote controller
    topo = ThreeLayerTopo()
    controller = RemoteController('c0', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=controller, switch=OVSKernelSwitch)

    # Start network
    net.start()
    print("*** Network started")

    # Wait for the network to stabilize
    time.sleep(20)

    # Initialize stats collection
    stats_data = []
    start_time = time.time()

    # Get hosts for traffic generation
    h1, h4 = net.get('h1', 'h4')
    h2, h5 = net.get('h2', 'h5')
    h3, h6 = net.get('h3', 'h6')

    # Generate varying amounts of traffic
    print("*** Generating traffic and collecting statistics...")
    try:
        # Start continuous pings with different intervals
        h1.cmd(f'ping -i 0.2 {h4.IP()} > /dev/null &')
        time.sleep(2)
        h2.cmd(f'ping -i 0.5 {h5.IP()} > /dev/null &')
        time.sleep(2)
        h3.cmd(f'ping -i 1.0 {h6.IP()} > /dev/null &')

        # Collect statistics
        for i in range(100):  # Collect 20 data points
            total_control = total_data = 0
            for s in ['s1', 's2', 's3', 's4', 's5']:
                c, d = collect_stats(s)
                total_control += c
                total_data += d
            stats_data.append((time.time() - start_time, total_control, total_data))
            print(f"Total Packets: {total_control + total_data}, Control: {total_control}, Data: {total_data}")
            time.sleep(2)

            # Add burst traffic every 5 iterations
            if i % 5 == 0:
                h1.cmd(f'ping -c 5 -i 0.1 {h4.IP()} > /dev/null &')

    except KeyboardInterrupt:
        pass
    finally:
        # Clean up background processes
        for h in [h1, h2, h3]:
            h.cmd('kill %ping')

        # Create the visualization
        print("*** Creating visualization...")
        plot_stats(stats_data)
        print("*** Graph saved as traffic_analysis.png")

        # Stop network
        net.stop()

if __name__ == '__main__':
    run_network()

