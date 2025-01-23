#!/usr/bin/python

from mininet.topo import Topo

class ThreeLayerTopo(Topo):
    "Three Layer Network Topology"

    def __init__(self):
        "Create three layer topo."

        # Initialize topology
        Topo.__init__(self)

        # Core Layer
        core = self.addSwitch('s1', dpid='0000000000000001')

        # Aggregation Layer
        agg1 = self.addSwitch('s2', dpid='0000000000000002')
        agg2 = self.addSwitch('s3', dpid='0000000000000003')

        # Access Layer
        access1 = self.addSwitch('s4', dpid='0000000000000004')
        access2 = self.addSwitch('s5', dpid='0000000000000005')

        # First establish all switch-to-switch connections
        
        # Core to Aggregation links
        self.addLink(core, agg1)    # s1-eth1 <-> s2-eth1
        self.addLink(core, agg2)    # s1-eth2 <-> s3-eth1

        # Aggregation redundancy link
        self.addLink(agg1, agg2)    # s2-eth2 <-> s3-eth2

        # Aggregation to Access links
        self.addLink(agg1, access1) # s2-eth3 <-> s4-eth1
        self.addLink(agg2, access1) # s3-eth3 <-> s4-eth2
        self.addLink(agg1, access2) # s2-eth4 <-> s5-eth1
        self.addLink(agg2, access2) # s3-eth4 <-> s5-eth2

        # Now add hosts and their connections
        hosts = []
        for i in range(1, 7):
            host = self.addHost(f'h{i}', 
                              ip=f'10.0.0.{i}/24',
                              mac=f'00:00:00:00:00:{i:02d}')
            hosts.append(host)

        # Connect hosts to access switches
        self.addLink(hosts[0], access1) # h1 <-> s4-eth3
        self.addLink(hosts[1], access1) # h2 <-> s4-eth4
        self.addLink(hosts[2], access1) # h3 <-> s4-eth5
        self.addLink(hosts[3], access2) # h4 <-> s5-eth3
        self.addLink(hosts[4], access2) # h5 <-> s5-eth4
        self.addLink(hosts[5], access2) # h6 <-> s5-eth5

topos = { 'threelayer': ( lambda: ThreeLayerTopo() ) }
