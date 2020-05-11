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
from opflex_integration_tests import logger
from tests import helper 

LOG = logger.get_logger(__name__)

def test_ping_within_epg(base_fixture):
    ep_list =[{'name': 'h1', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1'},
              {'name': 'h2', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.5',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1'}
             ]
    helper.create_ep(ep_list, base_fixture)
    helper.do_ping_ep(base_fixture, 'h1','h2')

@pytest.mark.skip(reason="Need to fix more infra")
def test_clusterip_service():
    utils.execute('curl http://10.1.0.100')
