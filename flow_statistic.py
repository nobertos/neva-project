import requests
from requests.auth import HTTPBasicAuth
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

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

# Retrieve flow statistics

# ONOS REST API details
host = "localhost"
port = "8181"
username = "karaf"
password = "karaf"
url = f"http://{host}:{port}/onos/v1/flows"

response = requests.get(url, auth=(username, password))

# Check response status
if response.status_code == 200:
    flow_data = response.json()
    print("Flow Statistics:")
    user_packets = {'count': 0, 'size': 0}
    useless_packets = {'count': 0, 'size': 0}
    for flow in flow_data['flows']:
        if flow['priority'] <= 40000:
            useless_packets['count'] += flow.get('packets', 'N/A')
            useless_packets['size'] += flow.get('bytes', 'N/A')
        else:
            user_packets['count'] += flow.get('packets', 'N/A')
            user_packets['size'] += flow.get('bytes', 'N/A')
    global_packets = useless_packets['count'] + user_packets['count']
    global_size = useless_packets['size'] + user_packets['size']
    print(f"Global number of packets: {global_packets}, Global size of packets: {global_size}")
    print(f"User number of packets: {user_packets['count']} ({round(user_packets['count'] / global_packets, 5) * 100}%), User size of packets: {user_packets['size']} ({round(user_packets['size'] / global_size, 5) * 100}%)")
    print(f"Useless number of packets: {useless_packets['count']} ({round(useless_packets['count'] / global_packets, 5) * 100}%), Useless size of packets: {useless_packets['size']} ({round(useless_packets['size'] / global_size, 5) * 100}%)")


    plot_packet_statistics(user_packets, useless_packets)
    print("\nGraphs have been saved to 'output_graphs.png'")


else:
    print(f"Failed to retrieve flow statistics. Status code: {response.status_code}, Message: {response.text}")
