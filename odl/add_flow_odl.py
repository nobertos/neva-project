# import requests
# import xml.etree.ElementTree as ET

# # ODL Controller Information
# ODL_IP = "127.0.0.1"  # Change to your controller's IP
# ODL_PORT = "8181"
# BASE_URL = f"http://{ODL_IP}:{ODL_PORT}/restconf/config/opendaylight-inventory:nodes/node"
# AUTH = ("admin", "admin")

# # Flow Definition in XML
# def create_flow_xml(flow_id, priority, ipv4_dst, output_port):
#     flow = ET.Element("flow", xmlns="urn:opendaylight:flow:inventory")
    
#     # Add flow details
#     ET.SubElement(flow, "id").text = str(flow_id)
#     ET.SubElement(flow, "priority").text = str(priority)
#     ET.SubElement(flow, "table_id").text = "0"
#     ET.SubElement(flow, "flow-name").text = f"Flow-{flow_id}"
    
#     # Match
#     match = ET.SubElement(flow, "match")
#     ethernet_match = ET.SubElement(match, "ethernet-match")
#     ethernet_type = ET.SubElement(ethernet_match, "ethernet-type")
#     ET.SubElement(ethernet_type, "type").text = "2048"  # IPv4
#     ET.SubElement(match, "ipv4-destination").text = ipv4_dst
    
#     # Instructions
#     instructions = ET.SubElement(flow, "instructions")
#     instruction = ET.SubElement(instructions, "instruction")
#     ET.SubElement(instruction, "order").text = "0"
#     apply_actions = ET.SubElement(instruction, "apply-actions")
#     action = ET.SubElement(apply_actions, "action")
#     ET.SubElement(action, "order").text = "0"
#     output_action = ET.SubElement(action, "output-action")
#     ET.SubElement(output_action, "output-node-connector").text = output_port
    
#     return ET.tostring(flow, encoding="unicode")

# # Push Flow to ODL
# def push_flow(node, flow_id, flow_xml):
#     url = f"{BASE_URL}/{node}/table/0/flow/{flow_id}"
#     headers = {"Content-Type": "application/xml"}
#     response = requests.put(url, auth=AUTH, data=flow_xml, headers=headers)
#     if response.status_code in [200, 201]:
#         print(f"Flow {flow_id} added successfully to {node}.")
#     else:
#         print(f"Failed to add flow {flow_id} to {node}. Status: {response.status_code}, Response: {response.text}")

# # Test Example Flows
# flow_xml = create_flow_xml(flow_id=1, priority=100, ipv4_dst="10.0.1.1/32", output_port="4")
# push_flow("openflow:1", 1, flow_xml)



# ------------------------- code 2 ------------------------

import requests
import xml.etree.ElementTree as ET

# ODL Controller Information
ODL_IP = "127.0.0.1"  # Change to your controller's IP
ODL_PORT = "8181"
BASE_URL = f"http://{ODL_IP}:{ODL_PORT}/restconf/config/opendaylight-inventory:nodes/node"
AUTH = ("admin", "admin")

# Function to create XML flow definition
def create_flow_xml(flow_id, table_id, priority, match_criteria, instructions):
    flow = ET.Element("flow", xmlns="urn:opendaylight:flow:inventory")
    ET.SubElement(flow, "id").text = str(flow_id)
    ET.SubElement(flow, "table_id").text = str(table_id)
    ET.SubElement(flow, "priority").text = str(priority)
    ET.SubElement(flow, "flow-name").text = f"Flow-{flow_id}"
    
    # Match criteria
    match = ET.SubElement(flow, "match")
    for criterion in match_criteria:
        if criterion["type"] == "ETH_TYPE":
            ethernet_match = ET.SubElement(match, "ethernet-match")
            ethernet_type = ET.SubElement(ethernet_match, "ethernet-type")
            ET.SubElement(ethernet_type, "type").text = criterion["ethType"]
        elif criterion["type"] == "IPV4_DST":
            ET.SubElement(match, "ipv4-destination").text = criterion["ip"]
        elif criterion["type"] == "IN_PORT":
            ET.SubElement(match, "in-port").text = criterion["port"]
    
    # Instructions
    instructions_xml = ET.SubElement(flow, "instructions")
    instruction = ET.SubElement(instructions_xml, "instruction")
    ET.SubElement(instruction, "order").text = "0"
    apply_actions = ET.SubElement(instruction, "apply-actions")
    for action in instructions:
        action_xml = ET.SubElement(apply_actions, "action")
        ET.SubElement(action_xml, "order").text = "0"
        if action["type"] == "OUTPUT":
            output_action = ET.SubElement(action_xml, "output-action")
            ET.SubElement(output_action, "output-node-connector").text = action["port"]
    
    return ET.tostring(flow, encoding="unicode")

# Function to push flow to ODL
def push_flow(node, flow_id, flow_xml):
    url = f"{BASE_URL}/{node}/table/0/flow/{flow_id}"
    headers = {"Content-Type": "application/xml"}
    response = requests.put(url, auth=AUTH, data=flow_xml, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Flow {flow_id} added successfully to {node}.")
    else:
        print(f"Failed to add flow {flow_id} to {node}. Status: {response.status_code}, Response: {response.text}")

# Example Rules
datapaths = ["openflow:1", "openflow:2", "openflow:3", "openflow:4", "openflow:5"]
flow_id = 1

for datapath in datapaths:
    if datapath.endswith("1"):  # Core switch
        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "1"}]
        action = [{"type": "OUTPUT", "port": "3"}]
        flow_xml = create_flow_xml(flow_id, 0, 100, match, action)
        push_flow(datapath, flow_id, flow_xml)
        flow_id += 1

        match = [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
        action = [{"type": "OUTPUT", "port": "1"}]
        flow_xml = create_flow_xml(flow_id, 0, 100, match, action)
        push_flow(datapath, flow_id, flow_xml)
        flow_id += 1

    elif datapath.endswith("4"):  # Access switch
        match = [{"type": "ETH_TYPE", "ethType": "0x0806"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}]
        action = [{"type": "OUTPUT", "port": "FLOOD"}]
        flow_xml = create_flow_xml(flow_id, 0, 60000, match, action)
        push_flow(datapath, flow_id, flow_xml)
        flow_id += 1

# Add rules for other switches as required...

# -----------------------code3------------------------
import requests
import xml.etree.ElementTree as ET

# ODL Controller Information
ODL_IP = "127.0.0.1"  # Change to your controller's IP
ODL_PORT = "8181"
BASE_URL = f"http://{ODL_IP}:{ODL_PORT}/restconf/config/opendaylight-inventory:nodes/node"
AUTH = ("admin", "admin")

# Function to create XML flow definition
def create_flow_xml(flow_id, table_id, priority, match_criteria, instructions):
    flow = ET.Element("flow", xmlns="urn:opendaylight:flow:inventory")
    ET.SubElement(flow, "id").text = str(flow_id)
    ET.SubElement(flow, "table_id").text = str(table_id)
    ET.SubElement(flow, "priority").text = str(priority)
    ET.SubElement(flow, "flow-name").text = f"Flow-{flow_id}"
    
    # Match criteria
    match = ET.SubElement(flow, "match")
    for criterion in match_criteria:
        if criterion["type"] == "ETH_TYPE":
            ethernet_match = ET.SubElement(match, "ethernet-match")
            ethernet_type = ET.SubElement(ethernet_match, "ethernet-type")
            ET.SubElement(ethernet_type, "type").text = criterion["ethType"]
        elif criterion["type"] == "IPV4_DST":
            ET.SubElement(match, "ipv4-destination").text = criterion["ip"]
        elif criterion["type"] == "IN_PORT":
            ET.SubElement(match, "in-port").text = criterion["port"]
    
    # Instructions
    instructions_xml = ET.SubElement(flow, "instructions")
    instruction = ET.SubElement(instructions_xml, "instruction")
    ET.SubElement(instruction, "order").text = "0"
    apply_actions = ET.SubElement(instruction, "apply-actions")
    for action in instructions:
        action_xml = ET.SubElement(apply_actions, "action")
        ET.SubElement(action_xml, "order").text = "0"
        if action["type"] == "OUTPUT":
            output_action = ET.SubElement(action_xml, "output-action")
            ET.SubElement(output_action, "output-node-connector").text = action["port"]
    
    return ET.tostring(flow, encoding="unicode")

# Function to push flow to ODL
def push_flow(node, flow_id, flow_xml):
    url = f"{BASE_URL}/{node}/table/0/flow/{flow_id}"
    headers = {"Content-Type": "application/xml"}
    response = requests.put(url, auth=AUTH, data=flow_xml, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Flow {flow_id} added successfully to {node}.")
    else:
        print(f"Failed to add flow {flow_id} to {node}. Status: {response.status_code}, Response: {response.text}")

# Switch Logic
datapaths = ["openflow:1", "openflow:2", "openflow:3", "openflow:4", "openflow:5"]
flow_id = 1

for datapath in datapaths:
    if datapath.endswith("1"):  # Core switch
        rules = [
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "1"}],
             [{"type": "OUTPUT", "port": "3"}], 100),
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "2"}],
             [{"type": "OUTPUT", "port": "3"}], 100),
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
             [{"type": "OUTPUT", "port": "1"}], 100),
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}],
             [{"type": "OUTPUT", "port": "2"}], 100),
        ]

    elif datapath.endswith("2") or datapath.endswith("3"):  # Aggregation switches
        rules = [
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "3"}],
             [{"type": "OUTPUT", "port": "1"}], 100),
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
             [{"type": "OUTPUT", "port": "3"}], 60000),
        ]

    elif datapath.endswith("4") or datapath.endswith("5"):  # Access switches
        rules = [
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}],
             [{"type": "OUTPUT", "port": "1"}], 100),
            ([{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
             [{"type": "OUTPUT", "port": "FLOOD"}], 60000),
            ([{"type": "ETH_TYPE", "ethType": "0x0806"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
             [{"type": "OUTPUT", "port": "FLOOD"}], 60000),
        ]

    # Add flows for the current datapath
    for match, actions, priority in rules:
        flow_xml = create_flow_xml(flow_id, 0, priority, match, actions)
        push_flow(datapath, flow_id, flow_xml)
        flow_id += 1
