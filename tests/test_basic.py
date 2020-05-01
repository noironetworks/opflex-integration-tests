#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
import sys
import time
import re
import pytest
from pyroute2 import netns
from opflex_integration_tests import utils
from tests import helper 

def test_ping_within_epg(ep_store):
    with open('/proc/self/ns/net', 'r') as fd, \
    open(helper.ep_netns('h1'), 'r') as ns_fd:
        netns.setns(ns_fd)
        helper.do_ping_ep(ep_store, 'h2')
        #utils.execute('/usr/bin/ping 10.0.0.5 -c 1')
        netns.setns(fd)

@pytest.mark.skip(reason="Need to fix more infra")
def test_clusterip_service():
    with open('/proc/self/ns/net', 'r') as fd, \
    open(helper.ep_netns('h1'), 'r') as ns_fd:
        netns.setns(ns_fd)
        utils.execute('curl http://10.1.0.100')
        netns.setns(fd)
