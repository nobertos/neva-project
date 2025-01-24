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
    for flow in flow_data['flows']:
        print(f"ID: {flow['selector']}, Bytes: {flow.get('bytes', 'N/A')}, Packets: {flow.get('packets', 'N/A')}")
else:
    print(f"Failed to retrieve flow statistics. Status code: {response.status_code}, Message: {response.text}")
