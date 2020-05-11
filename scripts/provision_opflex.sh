#! /bin/bash

echo "Provisioning opflex-integration-tests"

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

#Add the initial config for the bridges
sudo ovs-vsctl add-br br-int
sudo ovs-vsctl add-br br-access
sudo ovs-vsctl add-port br-int br0_vxlan0 -- set interface br0_vxlan0 type=vxlan options:remote_ip=flow options:key=flow
sudo ovs-vsctl add-port br-int gen1 -- set interface gen1 type=geneve options:remote_ip=flow options:key=1
sudo ovs-vsctl add-port br-access gen2 -- set interface gen2 type=geneve options:remote_ip=flow options:key=2

#Pick up the current integration tests repo 
sudo git clone https://github.com/noironetworks/opflex-integration-tests.git
pushd opflex-integration-tests/config
sudo cp opflex-agent-ovs.conf /etc/opflex-agent-ovs/
sudo rm -rf /etc/opflex-agent-ovs/plugins.conf.d/*
#Start opflex-agent
sudo systemctl start opflex-agent
#Start opflex_server
sudo /usr/bin/opflex_server --policy=./policy.json --daemon --log /var/log/opflex_server.log
popd

