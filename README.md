# opflex-integration-tests  
Integration test framework for opflex.  
These tests do not involve the fabric and are intended to test some of the  
features of opflex-agent on the datapath(openvswitch).

## Steps to run  

Clone opflex-integration-tests on the compute where the tests will run.  
```  
git clone https://github.com/noironetworks/opflex-integration-tests.git  
cd opflex-integration-tests  
```  

Install opflex-integration-tests. 
```  
sudo pip3 install -r requirements.txt  
```  

Ensure requirements for running opflex-agent are met. This section will be  
replaced by vagrant configuration.  
[Requirements for running opflex] https://github.com/noironetworks/opflex/blob/master/docs/building_and_running.md  

Copy the EP files from the config directory of this repo to the EP directory  
as configured in opflex-agent. Set the statistics interval in opflex-agent  
config to less than the STATS_TIME_DELAY setting in config/settings.toml.  
Create network namespaces with the same name as the EP file name  
(without the .ep extension), add veth pairs, patch ports for every EP.  
As an example:  
```
cat config/h1.ep
{  
    "policy-space-name": "test",  
    "endpoint-group-name": "group1",  
    "interface-name": "qpf-h1eth",  
    "access-interface":"h1eth",  
    "access-uplink-interface":"qpi-h1eth",  
    "ip": [  
        "10.0.0.4"  
    ],  
    "mac": "92:e2:9b:ad:0b:88",  
    "uuid": "83f18f0b-80f7-46e2-b06c-4d9487b0c754"  
}  

sudo ip netns add h1  
sudo ip link add name h1veth type veth peer name h1eth   
sudo ip link set dev h1veth up netns h1  
sudo ip netns exec h1 ifconfig lo up  
sudo ip netns exec h1 ipaddr add 10.0.0.4/24 dev h1veth  
sudo ifconfig h1eth up  

sudo ovs-vsctl add-port br-access h1eth  
sudo ovs-vsctl \  
 -- add-port br-access qpi-h1eth \  
 -- set interface qpi-h1eth type=patch options:peer=qpf-h1eth \  
 -- add-port br-int qpf-h1eth \  
 -- set interface qpf-h1eth type=patch options:peer=qpi-h1eth  

```  

Run opensvwitch and  opflex-agent. Run opflex-server with the policy.json file  
from the config directory.  

Finally, run tests with sudo python3 -m pytest or sudo pytest tests/test_basic.py.  
