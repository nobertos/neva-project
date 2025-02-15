#!/bin/bash

# Function to add OpenFlow rule
add_flow() {
    local switch=$1
    local priority=$2
    local match=$3
    local action=$4
    echo "Adding flow to $switch: match=($match) action=($action)"
    ovs-ofctl add-flow $switch -O openflow13 "priority=$priority,$match actions=$action"
}

# Core Switch (s1)
add_flow s1 500 "eth_type=0x0800,in_port=1" "output:3"
add_flow s1 500 "eth_type=0x0800,in_port=2" "output:3"
add_flow s1 500 "eth_type=0x0806,in_port=3" "output:4"
add_flow s1 500 "eth_type=0x0806,in_port=4" "output:3"
add_flow s1 500 "eth_type=0x0800,nw_dst=10.0.1.0/24" "output:1"
add_flow s1 500 "eth_type=0x0800,nw_dst=10.0.2.0/24" "output:2"
add_flow s1 500 "eth_type=0x0800,nw_dst=1.1.1.2" "output:4"  # Forward to Internet (hx3)
add_flow s1 500 "eth_type=0x0800,nw_dst=10.0.1.254" "output:3" # Forward to hx1
add_flow s1 500 "eth_type=0x0800,nw_dst=10.0.2.254" "output:2" # Forward to hx2

# Aggregation Switch 1 (s2)
add_flow s2 500 "eth_type=0x0800,in_port=3" "output:1"
add_flow s2 60000 "eth_type=0x0800,nw_dst=10.0.1.0/24" "output:3"  # Forward to Access Switch 1 (s4)
add_flow s2 60000 "eth_type=0x0800,nw_dst=10.0.2.0/24" "output:4"  # Forward to Access Switch 2 (s5)

# Aggregation Switch 2 (s3)
add_flow s3 500 "eth_type=0x0800,in_port=4" "output:1"
add_flow s3 60000 "eth_type=0x0800,nw_dst=10.0.2.0/24" "output:4"  # Forward to Access Switch 2 (s5)
add_flow s3 60000 "eth_type=0x0800,nw_dst=10.0.1.0/24" "output:3"  # Forward to Access Switch 1 (s4)

# Access Switch 1 (s4)
add_flow s4 500 "eth_type=0x0800" "output:1"
add_flow s4 60000 "eth_type=0x0800,nw_dst=10.0.2.0/24" "output:2"  # Forward to Access Switch 2 (s5)
add_flow s4 60000 "eth_type=0x0800,nw_dst=10.0.1.0/24" "output:FLOOD"  # Forward to all ports in 10.0.1.0/24 network
add_flow s4 60000 "eth_type=0x0806" "output:NORMAL"  # Handle ARP requests

# Access Switch 2 (s5)
add_flow s5 500 "eth_type=0x0800" "output:2"
add_flow s5 60000 "eth_type=0x0800,nw_dst=10.0.1.0/24" "output:1"  # Forward to Access Switch 1 (s4)
add_flow s5 60000 "eth_type=0x0800,nw_dst=10.0.2.0/24" "output:FLOOD"  # Forward to all ports in 10.0.2.0/24 network
add_flow s5 60000 "eth_type=0x0806" "output:NORMAL"  # Handle ARP requests

# Add default route for traffic to Internet via Core Switch
add_flow s1 1000 "eth_type=0x0800,nw_dst=0.0.0.0/0" "output:4"  # Default route to Internet via hx3
add_flow s2 1000 "eth_type=0x0800,nw_dst=0.0.0.0/0" "output:4"  # Default route to Internet via hx3
add_flow s3 1000 "eth_type=0x0800,nw_dst=0.0.0.0/0" "output:4"  # Default route to Internet via hx3

echo "OpenFlow rules applied successfully."

