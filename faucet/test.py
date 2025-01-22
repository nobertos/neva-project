from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch, OVSController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def create_network():
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

    info("*** Adding controller\n")
    c0 = net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    info("*** Adding switches\n")
    core = net.addSwitch('s1')
    agg1 = net.addSwitch('s2')
    agg2 = net.addSwitch('s3')

    info("*** Adding hosts\n")
    h1 = net.addHost('h1' )
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    info("*** Creating links\n")
    net.addLink(core, agg1)
    net.addLink(core, agg2)
    net.addLink(agg1, agg2)
    net.addLink(core, h1)
    net.addLink(agg1, h2)
    net.addLink(agg2, h3)

    info("*** Starting network\n")
    net.build()
    c0.start()
    core.start([c0])
    agg1.start([c0])
    agg2.start([c0])


    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
