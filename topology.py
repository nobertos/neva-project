#!/usr/bin/python

from mininet.topo import Topo

class ThreeLayerTopo(Topo):
    "Three Layer Network Topology"

    def __init__(self):
        "Create three layer topo."

        # Initialize topology
        Topo.__init__(self)

        # Add Core Switch
        core = self.addSwitch('s1', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='1')

        # Add Aggregation Switches
        agg1 = self.addSwitch('s2', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='2')
        agg2 = self.addSwitch('s3', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='3')


        # Add Access Switches
        access1 = self.addSwitch('s4', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='4')
        access2 = self.addSwitch('s5', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='5')

        # Add hosts (two hosts per access switch)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')

        # Add links between core and aggregation layers
        self.addLink(core, agg1)
        self.addLink(core, agg2)

        # Add links between aggregation switches (redundancy)
        self.addLink(agg1, agg2)

        # Add cross links between aggregation and access layers
        self.addLink(agg1, access1)
        self.addLink(agg1, access2)
        self.addLink(agg2, access1)
        self.addLink(agg2, access2)

        # Connect hosts to access switches
        self.addLink(access1, h1)
        self.addLink(access1, h2)
        self.addLink(access1, h3)
        self.addLink(access2, h4)
        self.addLink(access2, h5)
        self.addLink(access2, h6)

topos = { 'threelayer': ( lambda: ThreeLayerTopo() ) }
