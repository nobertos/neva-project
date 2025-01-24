import requests

# ODL Controller Information
ODL_IP = "127.0.0.1"
ODL_PORT = "8181"
BASE_URL = f"http://{ODL_IP}:{ODL_PORT}/restconf/config/opendaylight-inventory:nodes/node"
AUTH = ("admin", "admin")

# List of all switches in your topology
SWITCHES = [
    "openflow:1",  # Core switch
    "openflow:2",  # Aggregation 1
    "openflow:3",  # Aggregation 2
    "openflow:4",  # Access 1
    "openflow:5"   # Access 2
]

def delete_all_flows(switch):
    url = f"{BASE_URL}/{switch}/table/0"
    response = requests.delete(url, auth=AUTH)
    
    if response.status_code == 200:
        print(f"All flows deleted from {switch}")
    else:
        print(f"Failed to delete flows from {switch}. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# Delete flows from all switches
for switch in SWITCHES:
    delete_all_flows(switch)

print("Flow deletion process completed!")