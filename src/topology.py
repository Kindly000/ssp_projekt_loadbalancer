from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


class MinimalThreeTierTopo(Topo):
    def build(self):
        c1 = self.addSwitch("c1", dpid="0000000000000001", protocols="OpenFlow13")
        c2 = self.addSwitch("c2", dpid="0000000000000002", protocols="OpenFlow13")

        a1 = self.addSwitch("a1", dpid="0000000000000003", protocols="OpenFlow13")
        a2 = self.addSwitch("a2", dpid="0000000000000004", protocols="OpenFlow13")
        e1 = self.addSwitch("e1", dpid="0000000000000005", protocols="OpenFlow13")
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")

        a3 = self.addSwitch("a3", dpid="0000000000000006", protocols="OpenFlow13")
        a4 = self.addSwitch("a4", dpid="0000000000000007", protocols="OpenFlow13")
        e2 = self.addSwitch("e2", dpid="0000000000000008", protocols="OpenFlow13")
        h3 = self.addHost("h3", ip="10.0.0.3/24")
        h4 = self.addHost("h4", ip="10.0.0.4/24")

        for core in (c1, c2):
            for agg in (a1, a2, a3, a4):
                self.addLink(core, agg)

        for agg in (a1, a2):
            self.addLink(agg, e1)
        for agg in (a3, a4):
            self.addLink(agg, e2)

        self.addLink(e1, h1)
        self.addLink(e1, h2)
        self.addLink(e2, h3)
        self.addLink(e2, h4)


if __name__ == "__main__":
    setLogLevel("info")
    net = Mininet(
        topo=MinimalThreeTierTopo(),
        switch=OVSKernelSwitch,
        controller=lambda name: RemoteController(name, ip="127.0.0.1", port=6653),
        autoSetMacs=True,
    )
    net.start()
    CLI(net)
    net.stop()
