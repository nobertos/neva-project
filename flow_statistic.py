import requests
from requests.auth import HTTPBasicAuth

# ONOS REST API details
host = "localhost"
port = "8181"
username = "karaf"
password = "karaf"
url = f"http://{host}:{port}/onos/v1/flows"

# Retrieve flow statistics

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
else:
    print(f"Failed to retrieve flow statistics. Status code: {response.status_code}, Message: {response.text}")
