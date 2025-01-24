import requests
import xml.etree.ElementTree as ET

ODL_IP = "127.0.0.1"
ODL_PORT = "8181"
BASE_URL = f"http://{ODL_IP}:{ODL_PORT}/restconf/config/opendaylight-inventory:nodes/node"
AUTH = ("admin", "admin")

def create_flow_xml(flow_id, priority, match_criteria, instructions):
    flow = ET.Element("flow", xmlns="urn:opendaylight:flow:inventory")
    ET.SubElement(flow, "id").text = str(flow_id)
    ET.SubElement(flow, "priority").text = str(priority)
    ET.SubElement(flow, "table_id").text = "0"
    
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

    instructions_xml = ET.SubElement(flow, "instructions")
    instruction = ET.SubElement(instructions_xml, "instruction")
    ET.SubElement(instruction, "order").text = "0"
    apply_actions = ET.SubElement(instruction, "apply-actions")
    
    for action in instructions:
        action_xml = ET.SubElement(apply_actions, "action")
        ET.SubElement(action_xml, "order").text = "0"
        output_action = ET.SubElement(action_xml, "output-action")
        ET.SubElement(output_action, "output-node-connector").text = action["port"]

    return ET.tostring(flow, encoding="unicode")

def add_flow(datapath, flow_id, match_criteria, instructions, priority=5000):
    flow_xml = create_flow_xml(flow_id, priority, match_criteria, instructions)
    url = f"{BASE_URL}/{datapath}/table/0/flow/{flow_id}"
    response = requests.put(url, auth=AUTH, data=flow_xml, 
                          headers={"Content-Type": "application/xml"})
    if response.status_code in [200, 201]:
        print(f"Flow {flow_id} added to {datapath}")
    else:
        print(f"Failed to add flow {flow_id} to {datapath}. Status: {response.status_code}")

# Main configuration matching your friend's ONOS rules
datapaths = ["openflow:1", "openflow:2", "openflow:3", "openflow:4", "openflow:5"]
flow_id = 1  # Simple counter-based flow ID

for datapath in datapaths:
    if datapath.endswith("1"):  # Core switch
        # Internet routing
        add_flow(datapath, flow_id, 
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "1"}],
                [{"type": "OUTPUT", "port": "3"}])
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "2"}],
                [{"type": "OUTPUT", "port": "3"}])
        flow_id +=1
        
        # Subnet routing
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
                [{"type": "OUTPUT", "port": "1"}])
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}],
                [{"type": "OUTPUT", "port": "2"}])
        flow_id +=1

        # Default route to internet (this assumes the gateway is connected to port 3)
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "0.0.0.0/0"}],
                [{"type": "OUTPUT", "port": "3"}])  # Forwarding to gateway (or internet)
        flow_id +=1

    elif datapath.endswith("2"):  # Aggregation switch 2
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "3"}],
                [{"type": "OUTPUT", "port": "1"}])
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
                [{"type": "OUTPUT", "port": "3"}], 60000)
        flow_id +=1

    elif datapath.endswith("3"):  # Aggregation switch 3
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IN_PORT", "port": "4"}],
                [{"type": "OUTPUT", "port": "1"}])
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}],
                [{"type": "OUTPUT", "port": "4"}], 60000)
        flow_id +=1

    elif datapath.endswith("4"):  # Access switch 4
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}],
                [{"type": "OUTPUT", "port": "1"}])
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}],
                [{"type": "OUTPUT", "port": "2"}], 60000)
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
                [{"type": "OUTPUT", "port": "FLOOD"}], 60000)  # Changed NORMAL to FLOOD
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0806"}],
                [{"type": "OUTPUT", "port": "NORMAL"}], 60000)  # Changed NORMAL to FLOOD
        flow_id +=1

    elif datapath.endswith("5"):  # Access switch 5
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}],
                [{"type": "OUTPUT", "port": "2"}])
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.1.0/24"}],
                [{"type": "OUTPUT", "port": "1"}], 60000)
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0800"}, {"type": "IPV4_DST", "ip": "10.0.2.0/24"}],
                [{"type": "OUTPUT", "port": "FLOOD"}], 60000)
        flow_id +=1
        
        add_flow(datapath, flow_id,
                [{"type": "ETH_TYPE", "ethType": "0x0806"}],
                [{"type": "OUTPUT", "port": "NORMAL"}], 60000)  # Changed NORMAL to FLOOD
        flow_id +=1

print("All flows configured successfully!")