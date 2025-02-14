
total_packets = 0
total_bytes = 0

with open('flow_stats.txt', 'r') as f:
    content = f.read()
    
    # Sum up packets and bytes
    for flow in content.split('\n'):
        if 'n_packets=' in flow:
            try:
                packets = int(flow.split('n_packets=')[1].split(',')[0])
                bytes_count = int(flow.split('n_bytes=')[1].split(',')[0])
                total_packets += packets
                total_bytes += bytes_count
            except (IndexError, ValueError):
                continue

print(f"\nTotal Statistics:")
print(f"Total Packets: {total_packets}")
print(f"Total Bytes: {total_bytes}")
