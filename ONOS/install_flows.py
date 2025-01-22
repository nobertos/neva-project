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

for datapath in datapaths:
    f = {}
    f["priority"] = 50000
    f["timeout"] = 0
    f["isPermanent"] = True
    f["deviceId"] = datapath
    f["selector"] = {}
    f["selector"]["criteria"] = []
    f["selector"]["criteria"].append({"type": "ETH_TYPE", "ethType": "0x0800"})
    f["treatment"] = {}
    f["treatment"]["instructions"] = []
    f["treatment"]["instructions"].append({"type": "OUTPUT", "port": "CONTROLLER"})
    flows.append(f)

resp = requests.post(
    url,
    json={"flows": flows},
    auth=(username, password)
)
print(resp.text)
