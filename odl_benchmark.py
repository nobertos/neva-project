from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from time import sleep
import subprocess
import os

def analyze_pcap(file_path):
    """Analyze a pcap file to count packets and calculate total size."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return 0, 0

    try:
        # Check if tshark is installed
        subprocess.check_call(["tshark", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("tshark is not installed. Please install it using 'sudo apt-get install tshark'.")
        return 0, 0

    try:
        # Use tshark to count packets
        packet_count = int(subprocess.check_output(
            f"tshark -r {file_path} -T fields -e frame.number | wc -l", shell=True
        ))
        # Use tshark to calculate total size
        total_size = int(subprocess.check_output(
            f"tshark -r {file_path} -T fields -e frame.len | awk '{{sum+=$1}} END {{print sum}}'", shell=True
        ))
        return packet_count, total_size
    except subprocess.CalledProcessError:
        print(f"Error analyzing {file_path}")
        return 0, 0
    except ValueError:
        print(f"No packets found in {file_path}")
        return 0, 0

def calculate_packet_loss(ping_output):
    """Calculate packet loss from ping output."""
    lines = ping_output.splitlines()
    if not lines:
        return 0.0
    # Extract packet loss percentage from the last line of ping output
    last_line = lines[-1]
    if "packet loss" in last_line:
        loss_percentage = float(last_line.split("%")[0].split()[-1])
        return loss_percentage
    return 0.0

def calculate_delay(pcap_file1, pcap_file2):
    """Calculate delay between two pcap files."""
    if not os.path.exists(pcap_file1) or not os.path.exists(pcap_file2):
        print(f"One or both files do not exist: {pcap_file1}, {pcap_file2}")
        return 0.0

    try:
        # Extract timestamps from the first pcap file
        timestamps1 = subprocess.check_output(
            f"tshark -r {pcap_file1} -T fields -e frame.time_epoch", shell=True
        ).decode().splitlines()
        # Extract timestamps from the second pcap file
        timestamps2 = subprocess.check_output(
            f"tshark -r {pcap_file2} -T fields -e frame.time_epoch", shell=True
        ).decode().splitlines()
        if not timestamps1 or not timestamps2:
            return 0.0
        # Calculate average delay
        delay = float(timestamps2[0]) - float(timestamps1[0])
        return delay
    except subprocess.CalledProcessError:
        print(f"Error calculating delay between {pcap_file1} and {pcap_file2}")
        return 0.0

def calculate_statistics():
    """Calculate statistics from tcpdump capture files."""
    user_packets = {'count': 0, 'size': 0}
    useless_packets = {'count': 0, 'size': 0}

    # Analyze host capture files
    for i in range(1, 7):
        file_path = f"h{i}.pcap"
        packet_count, total_size = analyze_pcap(file_path)
        if i <= 3:
            user_packets['count'] += packet_count
            user_packets['size'] += total_size
        else:
            useless_packets['count'] += packet_count
            useless_packets['size'] += total_size

    # Analyze switch capture files
    switches = ['s1', 's2', 's3']
    for sw in switches:
        for eth in range(1, 5):
            file_path = f"{sw}-eth{eth}.pcap"
            packet_count, total_size = analyze_pcap(file_path)
            useless_packets['count'] += packet_count
            useless_packets['size'] += total_size

    # Calculate global statistics
    global_packets = user_packets['count'] + useless_packets['count']
    global_size = user_packets['size'] + useless_packets['size']

    if global_packets == 0 or global_size == 0:
        print("No packets found in capture files.")
        return

    # Print statistics
    print(f"Global number of packets: {global_packets}, Global size of packets: {global_size}")
    print(f"User number of packets: {user_packets['count']} ({round(user_packets['count'] / global_packets, 5) * 100}%), User size of packets: {user_packets['size']} ({round(user_packets['size'] / global_size, 5) * 100}%)")
    print(f"Useless number of packets: {useless_packets['count']} ({round(useless_packets['count'] / global_packets, 5) * 100}%), Useless size of packets: {useless_packets['size']} ({round(useless_packets['size'] / global_size, 5) * 100}%)")

    # Calculate packet loss from ping tests
    with open("ping_h1_h2.txt", "r") as f:
        ping_output = f.read()
    packet_loss = calculate_packet_loss(ping_output)
    print(f"Packet Loss (h1 -> h2): {packet_loss}%")

    # Calculate delay between h1 and h2
    delay = calculate_delay("h1.pcap", "h2.pcap")
    print(f"Delay (h1 -> h2): {delay:.6f} seconds")

def setup_network():
    net = Mininet(controller=None, switch=OVSSwitch)

    print(" Adding Remote Controller (ODL)")
    c0 = net.addController('c0', controller=RemoteController, ip="127.0.0.1", port=6653)

    print("🖧 Creating Tree Topology (depth=3, fanout=2)")
    net.addSwitch('s1', protocols="OpenFlow13")  # Core switch
    net.addSwitch('s2', protocols="OpenFlow13")  # Aggregation switch 1
    net.addSwitch('s3', protocols="OpenFlow13")  # Aggregation switch 2
    net.addSwitch('s4', protocols="OpenFlow13")  # Access switch 1
    net.addSwitch('s5', protocols="OpenFlow13")  # Access switch 2
    net.addSwitch('s6', protocols="OpenFlow13")  # Access switch 3
    net.addSwitch('s7', protocols="OpenFlow13")  # Access switch 4

    # Connect core to aggregation
    net.addLink('s1', 's2')
    net.addLink('s1', 's3')

    # Connect aggregation to access
    net.addLink('s2', 's4')
    net.addLink('s2', 's5')
    net.addLink('s3', 's6')
    net.addLink('s3', 's7')

    # Add hosts
    for i in range(1, 7):
        host = net.addHost(f'h{i}', ip=f"10.0.0.{i}")
        if i <= 3:
            net.addLink(host, 's4')  # Connect first 3 hosts to s4
        else:
            net.addLink(host, 's5')  # Connect last 3 hosts to s5

    print(" Starting Network")
    net.start()

    print("Running Benchmarks...")

    # Start tcpdump on hosts
    hosts = [f'h{i}' for i in range(1, 7)]
    for host in hosts:
        print(f"Starting tcpdump on {host}")
        net.get(host).cmd(f"tcpdump -i {host}-eth0 -w {host}.pcap &")

    # Start tcpdump on switches
    switches = ['s1', 's2', 's3']
    for sw in switches:
        for eth in range(1, 5):
            print(f"Starting tcpdump on {sw}-eth{eth}")
            net.get(sw).cmd(f"tcpdump -i {sw}-eth{eth} -w {sw}-eth{eth}.pcap &")

    # Start iperf servers
    print("Starting iperf servers...")
    net.get('h2').cmd("iperf -s &")
    net.get('h5').cmd("iperf -s &")
    sleep(3)  # Wait for servers to start

    # Start iperf clients
    print("Starting iperf clients...")
    net.get('h1').cmd("iperf -c 10.0.0.2 -t 30 &")
    net.get('h4').cmd("iperf -c 10.0.0.5 -t 30 &")
    net.get('h3').cmd("iperf -c 10.0.0.5 -t 30 &")
    net.get('h6').cmd("iperf -c 10.0.0.2 -t 30 &")

    # Perform ping tests
    print("Performing ping tests...")
    net.get('h1').cmd("ping -c 5 10.0.0.2 > ping_h1_h2.txt &")
    net.get('h4').cmd("ping -c 5 10.0.0.5 > ping_h4_h5.txt &")
    net.get('h3').cmd("ping -c 5 10.0.0.6 > ping_h3_h6.txt &")

    print("Benchmarks Running...")
    sleep(35)  # Wait for benchmarks to complete (30s for iperf + buffer)

    # Stop tcpdump processes
    for host in hosts:
        net.get(host).cmd("pkill tcpdump")
    for sw in switches:
        for eth in range(1, 5):
            net.get(sw).cmd("pkill tcpdump")

    # Analyze tcpdump files and calculate statistics
    print("Analyzing tcpdump files...")
    calculate_statistics()

    # Open CLI for interaction
    CLI(net)

    print("Stopping Network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()
