import copy
import json
import requests


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


# REST API url and headers
host = "localhost"
port = "8181"
username = "karaf"
password = "karaf"

url = f"http://{host}:{port}/onos/v1/devices"

# Retrieve device IDs 

response = requests.get(url, auth=(username, password))
if response.status_code == 200:
    device_data = response.json()['devices']
    datapaths = [device['id'] for device in device_data]
    

    # Post flows
    url = f"http://{host}:{port}/onos/v1/flows"
    headers = {'Content-type': 'application/json'}
    
    flows = []
    flow = {"priority": 50000, "timeout": 0, "isPermanent": True, "deviceId": "", 
            "treatment": {"instructions": []}, "selector": {"criteria": []}}

   
    for datapath in datapaths:
        if datapath.endswith("100"):  # L2 switch
            # ARP 
            match = [{"type": "ETH_TYPE", "ethType": "0x0806"}]
            action = [{"type": "OUTPUT", "port": "NORMAL"}]
            add_flow(datapath, criterias=match, instructions=action, priority=60000)
            # To internet
            action = [{"type": "OUTPUT", "port": "3"}]
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "1"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "2"}]
            add_flow(datapath, criterias=match, instructions=action)
            # From internet
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "3"}]
            action = [{"type": "OUTPUT", "port": "1"}]
            add_flow(datapath, criterias=match, instructions=action)
            action = [{"type": "OUTPUT", "port": "2"}]
            add_flow(datapath, criterias=match, instructions=action)

        elif datapath[-2] == "0":  # core switches
            # routing to internet
            action = [{"type": "OUTPUT", "port": "6"}]

            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "2"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "3"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "4"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "5"}]
            add_flow(datapath, criterias=match, instructions=action)

            # routing to hosts
            # go to aggregation 1
            action = [{"type": "OUTPUT", "port": "2"}]
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)

            # go to aggregation 2
            action = [{"type": "OUTPUT", "port": "3"}]
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.3.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.4.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)

            # go to aggregation 3
            action = [{"type": "OUTPUT", "port": "4"}]
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.5.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.6.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)

            # go to aggregation 4
            action = [{"type": "OUTPUT", "port": "5"}]
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.7.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.8.0/24"}]
            add_flow(datapath, criterias=match, instructions=action)

        elif datapath[-2] == "1":  # aggregation switches
            # routing to internet
            action = [{"type": "OUTPUT", "port": "1"}]

            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "6"}]
            add_flow(datapath, criterias=match, instructions=action)
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "7"}]
            add_flow(datapath, criterias=match, instructions=action)

            # routing to his hosts
            num_switch = int(datapath[-1])

            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": f"10.0.{num_switch * 2 -1}.0/24"}]
            action = [{"type": "OUTPUT", "port": "6"}]
            add_flow(datapath, criterias=match, instructions=action, priority=60000)

            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": f"10.0.{num_switch * 2}.0/24"}]
            action = [{"type": "OUTPUT", "port": "7"}]
            add_flow(datapath, criterias=match, instructions=action, priority=60000)

            # routing to other hosts (extreme neighbors)
            if num_switch <= 2:  # s11 and s12 want to reach these IPs
                ip = ['5', '6', '7', '8']
            else:  # s13 and s14 want to reach these IPs
                ip = ['1', '2', '3', '4']
            
            for i in range(2):
                action = [{"type": "OUTPUT", "port": f"{4 + i}"}]  # route to each subnet's aggregation switch

                match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": f"10.0.{ip[i * 2]}.0/24"}]
                add_flow(datapath, criterias=match, instructions=action, priority=60000)

                match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": f"10.0.{ip[i * 2 + 1]}.0/24"}]
                add_flow(datapath, criterias=match, instructions=action, priority=60000)
            
        elif datapath[-2] == "2":  # access switches
            # routing to internet, closest neighbors and extreme neighbors
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}]
            action = [{"type": "OUTPUT", "port": "1"}]
            add_flow(datapath, criterias=match, instructions=action)

            # routing to other hosts (close neighbors)
            num_switch = int(datapath[-1])
            if num_switch <= 2:  # s21 and s22 want to reach these IPs
                ip = ['3', '4']
            elif num_switch <= 4:  # s23 and s24 want to reach these IPs
                ip = ['1', '2']
            elif num_switch <= 6:  # s25 and s26 want to reach these IPs
                ip = ['7', '8'] 
            else:  # s27 and s28 want to reach these IPs
                ip = ['5', '6']
            
            action = [{"type": "OUTPUT", "port": "2"}]  # route to each subnet's aggregation switch
            for i in range(2):
                match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": f"10.0.{ip[i]}.0/24"}]
                add_flow(datapath, criterias=match, instructions=action, priority=60000)

            # routing to his hosts
            match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": f"10.0.{num_switch}.0/24"}]
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
