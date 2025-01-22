#!/usr/bin/python3
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def createNetwork():
    # Create an empty network
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

    # Add remote controller (Faucet)
    c0 = net.addController('c0', controller=RemoteController, ip='localhost', port=6653)

    # Add switches with specific dpids (using 16-char hex format)
    # core
    s1 = net.addSwitch('s1', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='1')
    # aggregation   
    s2 = net.addSwitch('s2', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='2')
    s3 = net.addSwitch('s3', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='3')
    # access
    s4 = net.addSwitch('s4', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='4')
    s5 = net.addSwitch('s5', protocols='OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15', dpid='5')

    # Add hosts with specific IP addresses
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')

    # Add links between switches
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s2, s3)
    net.addLink(s2, s4)
    net.addLink(s2, s5)
    net.addLink(s3, s4)
    net.addLink(s3, s5)

    # Add links between hosts and switches
    net.addLink(h1, s4)
    net.addLink(h2, s4)
    net.addLink(h3, s4)
    net.addLink(h4, s5)
    net.addLink(h5, s5)

    # Build and start network
    net.build()
    c0.start()


    # Enter CLI for further debugging if needed
    CLI(net)

    # Clean up
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createNetwork()
