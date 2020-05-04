#! /bin/bash
set +e
#Pick up the current deb package for opflex
pushd /vagrant/data
#Install libopflex
find . -name "libopflex_*deb" | awk '{system("sudo dpkg -i "$1)}'
#Install libmodelgbp
find . -name "libmodelgbp_*deb" | awk '{system("sudo dpkg -i "$1)}'
#Install libopflex-agent
find . -name "libopflex-agent_*deb" | awk '{system("sudo dpkg -i "$1)}'
#Install libopflex-agent-dev for opflex_server
find . -name "libopflex-agent-dev_*deb" | awk '{system("sudo dpkg -i "$1)}'
#Install opflex-agent
find . -name "opflex-agent_*deb" | awk '{system("sudo dpkg -i "$1)}'
#Install renderer
find . -name "opflex-agent-renderer-openvswitch_*deb" | awk '{system("sudo dpkg -i "$1)}'
sudo systemctl stop opflex-agent
popd

#Port addition corresponding to EP
add_port() {
    sudo ip netns add $1
    veth_peer=$(echo `echo $1veth`| tr "[:upper:]" "[:lower:]")
    eth_peer=$(echo `echo $1eth`| tr "[:upper:]" "[:lower:]")
    sudo ip link add name $eth_peer type veth peer name $veth_peer
    sudo ip link set dev $veth_peer up netns $1
    sudo ip netns exec $1 ifconfig lo up
    sudo ifconfig $eth_peer up
    sudo ip netns exec $1 ip addr add $2 dev $veth_peer 
    sudo ovs-vsctl add-port br-access $eth_peer
    sudo ovs-vsctl \
     -- add-port br-access qpi-$eth_peer \
     -- set interface qpi-$eth_peer type=patch options:peer=qpf-$eth_peer \
     -- add-port br-int qpf-$eth_peer \
     -- set interface qpf-$eth_peer type=patch options:peer=qpi-$eth_peer
}

#Add the initial config for the bridges
sudo ovs-vsctl add-br br-int
sudo ovs-vsctl add-br br-access
sudo ovs-vsctl add-port br-int br0_vxlan0 -- set interface br0_vxlan0 type=vxlan options:remote_ip=flow options:key=flow
sudo ovs-vsctl add-port br-int gen1 -- set interface gen1 type=geneve options:remote_ip=flow options:key=1
sudo ovs-vsctl add-port br-access gen2 -- set interface gen2 type=geneve options:remote_ip=flow options:key=2

#Pick up the current integration tests repo 
sudo git clone https://github.com/noironetworks/opflex-integration-tests.git
#Add the Eps related to the tests
pushd opflex-integration-tests/config
sudo cp opflex-agent-ovs.conf /etc/opflex-agent-ovs/
sudo rm -rf /etc/opflex-agent-ovs/plugins.conf.d/*
sudo systemctl start opflex-agent
for file in *; do
	if [[ $(echo $file | grep ".ep$") == $file ]] ; then
		ip_address=$(../scripts/get_address.py $file)
		echo $ip_address
		ep=$(echo $file | awk -F'.' '{print $1}')
		echo $ep
		add_port $ep $ip_address
	fi
done
#Start opflex_server
sudo /usr/bin/opflex_server --policy=./policy.json --daemon --log /var/log/opflex_server.log
popd

