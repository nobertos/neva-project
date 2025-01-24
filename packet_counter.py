import os
"""from scapy.all import rdpcap
from collections import Counter

def analyze_pcap(file_path):
    # Read packets from the pcap file
    packets = rdpcap(file_path)

    # Initialize a Counter to count packet types
    packet_stats = Counter()

    # Iterate through packets
    for packet in packets:
        if packet.haslayer('ARP'):
            packet_stats['ARP'] += 1
        elif packet.haslayer('IP'):
            if packet.haslayer('TCP'):
                packet_stats['TCP'] += 1
            elif packet.haslayer('UDP'):
                packet_stats['UDP'] += 1
            elif packet.haslayer('ICMP'):
                packet_stats['ICMP'] += 1
            else:
                packet_stats['Other IP'] += 1
        else:
            packet_stats['Non-IP'] += 1

    # Print the statistics
    print(f"Packet Statistics for {file_path}:")
    for packet_type, count in packet_stats.items():
        print(f"{packet_type}: {count}")"""

from scapy.all import rdpcap
from collections import defaultdict

def analyze_pcap(file_path):
    # Read packets from the pcap file
    packets = rdpcap(file_path)
    
    # Initialize statistics
    packet_stats = defaultdict(lambda: {'count': 0, 'size': 0})

    # Analyze packets
    for packet in packets:
        # Get the packet type (protocol/layer)
        if packet.haslayer('ARP'):
            packet_type = "ARP"
        elif packet.haslayer('IP'):
            if packet.haslayer('TCP'):
                packet_type = "TCP"
            elif packet.haslayer('UDP'):
                packet_type = "UDP"
            elif packet.haslayer('ICMP'):
                packet_type = "ICMP"
            else:
                packet_type = "Other IP"
        else:
            packet_type = "Non-IP"
        
        # Update statistics
        packet_stats[packet_type]['count'] += 1
        global_stats[packet_type]['count'] += 1
        packet_stats[packet_type]['size'] += len(packet)
        global_stats[packet_type]['size'] += len(packet)
    
    # Print statistics
    print(f"Statistics for {file_path}:")
    print(f"{'Packet Type':<20} {'Count':<10} {'Total Size (bytes)':<20}")
    print("-" * 50)
    for packet_type, stats in packet_stats.items():
        print(f"{packet_type:<20} {stats['count']:<10} {stats['size']:<20}")
    
    return packet_stats

if __name__ == '__main__':
    # Path to your pcap file
    global_stats = defaultdict(lambda: {'count': 0, 'size': 0})
    global_packets = 0
    global_size = 0
    for file in os.listdir("."):
        if file.endswith('.pcap'):
            stats = analyze_pcap(file)
            print()
            global_packets += sum(stats[x]["count"] for x in stats)
            global_size += sum(stats[x]["size"] for x in stats)
    print(f"GLOBAL: Number of packets -> {global_packets}, Size of packets -> {global_size}")
    print(f"{'Packet Type':<20} {'Count':<10}(%){' ':<7} {'Total Size (bytes)':<20}(%)")
    print("-" * 50)
    for packet_type, stats in global_stats.items():
        print(f"{packet_type:<20} {stats['count']:<10}{round((stats['count'] / global_packets) * 100, 5):<10} {stats['size']:<20}{round((stats['size'] / global_size) * 100, 5):<10}")
