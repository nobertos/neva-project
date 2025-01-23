import copy
import json
import requests

# REST API url and headers
host = "localhost"
port = "8181"
username = "karaf"
password = "karaf"
url = f"http://{host}:{port}/onos/v1/flows"
headers = {'Content-type': 'application/json'}

datapaths = ["of:0000000000000005", "of:0000000000000004", "of:0000000000000003", "of:0000000000000002", "of:0000000000000001"]
flows = []
flow = {"priority": 50000, "timeout": 0, "isPermanent": True, "deviceId": "", 
        "treatment": {"instructions": []}, "selector": {"criteria": []}}

def add_flow(dp, criterias, instructions, priority=50000):
    """"creates a new flow with the provided list of dictionaries of criterias and instructions
    and adds them to the list of flows (global variable)"""
    f = {}
    f["priority"] = priority
    f["timeout"] = 0
    f["isPermanent"] = True
    f["deviceId"] = dp
    f["selector"] = {}
    f["selector"]["criteria"] = []
    f["treatment"] = {}
    f["treatment"]["instructions"] = []
    for criteria in criterias:
        f["selector"]["criteria"].append(criteria)
    for instruction in instructions:
        f["treatment"]["instructions"].append(instruction)
    flows.append(f)

for datapath in datapaths:
    if datapath.endswith("1"):  # core switch
        # routing to internet
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "1"}]
        action = [{"type": "OUTPUT", "port": "3"}]
        add_flow(datapath, criterias=match, instructions=action)
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "2"}]
        action = [{"type": "OUTPUT", "port": "3"}]
        add_flow(datapath, criterias=match, instructions=action)
        # routing to hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
        action = [{"type": "OUTPUT", "port": "1"}]
        add_flow(datapath, criterias=match, instructions=action)
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}]
        action = [{"type": "OUTPUT", "port": "2"}]
        add_flow(datapath, criterias=match, instructions=action)

    elif datapath.endswith("2"):  # aggregation switch
        # routing to internet
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "3"}]
        action = [{"type": "OUTPUT", "port": "1"}]
        add_flow(datapath, criterias=match, instructions=action)
        # routing to his hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
        action = [{"type": "OUTPUT", "port": "3"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
    
    elif datapath.endswith("3"):  # aggregation switch
        # routing to internet
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "4"}]
        action = [{"type": "OUTPUT", "port": "1"}]
        add_flow(datapath, criterias=match, instructions=action)
        # routing to his hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}]
        action = [{"type": "OUTPUT", "port": "4"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
    
    elif datapath.endswith("4"):  # access switch
        # routing to internet
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}]
        action = [{"type": "OUTPUT", "port": "1"}]
        add_flow(datapath, criterias=match, instructions=action)
        # routing to other hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}]
        action = [{"type": "OUTPUT", "port": "2"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
        # routing to his hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
        action = [{"type": "OUTPUT", "port": "FLOOD"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
        match = [{"type": "ETH_TYPE", "ethType": "0x0806"}]
        action = [{"type": "OUTPUT", "port": "NORMAL"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
    
    elif datapath.endswith("5"):  # access switch
        # routing to internet
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}]
        action = [{"type": "OUTPUT", "port": "2"}]
        add_flow(datapath, criterias=match, instructions=action)
        # routing to other hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
        action = [{"type": "OUTPUT", "port": "1"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
        # routing to his hosts
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}]
        action = [{"type": "OUTPUT", "port": "FLOOD"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)
        match = [{"type": "ETH_TYPE", "ethType": "0x0806"}]
        action = [{"type": "OUTPUT", "port": "NORMAL"}]
        add_flow(datapath, criterias=match, instructions=action, priority=60000)

resp = requests.post(
    url,
    json={"flows": flows},
    auth=(username, password)
)
print(resp.text)
