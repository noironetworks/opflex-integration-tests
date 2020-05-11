# opflex-integration-tests  
Integration test framework for opflex.  
These tests do not involve the fabric and are intended to test some of the  
features of opflex-agent on the datapath(openvswitch).

## Steps to run  

Clone opflex-integration-tests on the compute where the tests will run.  
```  
git clone https://github.com/noironetworks/opflex-integration-tests.git  
cd opflex-integration-tests/scripts  
mkdir data 
```  
Copy the opflex deb packages you want to test to the data directory that was created above.  Install virtual box and vagrant on the host machine. Tests will run inside the vagrant machine.

```
vagrant up
vagrant ssh
pushd /home/vagrant/opflex-integration-tests
sudo pytest
```  

Last command runs the test. All the test options available with pytest can be used.  
eg. sudo pytest -x runs with stop on failure.  
