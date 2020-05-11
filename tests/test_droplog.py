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
import logging
import os
import sys
import time
import re
import pytest
from pyroute2 import netns
from opflex_integration_tests import utils
from opflex_integration_tests import logger
from tests import helper
from dynaconf import settings
from scapy.all import *

STATS_TIMER_DELAY = settings.STATS_TIMER_DELAY
UNKNOWN_MAC = "00:01:02:03:04:05"
BCAST_MAC = "ff:ff:ff:ff:ff:ff"
UNKNOWN_IP = "10.1.2.3"

LOG = logger.get_logger(__name__)

def test_security_table_drop(base_fixture):
    ep_list =[{'name': 'h5', 'virt_router_ip': '12.0.0.1', 'ip': '12.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group5',\
               'disable_ipv6': True},
              {'name': 'h6', 'virt_router_ip': '12.0.0.1', 'ip': '12.0.0.5',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group5', \
               'disable_ipv6': True}
             ]
    helper.create_ep(ep_list, base_fixture)
    currDropCount = helper.get_table_drop_counter(1)
    currPromDropCount = helper.get_prometheus_table_drop_counter('PORT_SECURITY_TABLE')
    scapy_cmd = "sendp(Ether(src=\"{}\",dst=\"{}\")/IP(dst=\"{}\"))".\
    format(UNKNOWN_MAC, BCAST_MAC, base_fixture['eps']['h5']['ip'])
    LOG.info("scapy_cmd=%s" % scapy_cmd)
    helper.do_run_scapy_cmd('h6', scapy_cmd)
    time.sleep(STATS_TIMER_DELAY)
    newDropCount = helper.get_table_drop_counter(1)
    newPromDropCount = helper.get_prometheus_table_drop_counter('PORT_SECURITY_TABLE')
    assert((currDropCount+1)==newDropCount)
    assert((currPromDropCount+1)==newPromDropCount)

# Send a packet with unknown dst MAC
@pytest.mark.skip(reason="Behavior is to tunnel to uplink")
def test_route_table_drop(base_fixture):
    ep_list =[{'name': 'h1', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1'}
             ]
    helper.create_ep(ep_list, base_fixture)
    currDropCount = helper.get_table_drop_counter(7)
    currPromDropCount = helper.get_prometheus_table_drop_counter('ROUTE_TABLE')
    scapy_cmd = "sendp(Ether(src=\"{}\",dst=\"{}\")/IP(dst=\"{}\",src=\"{}\"))".\
    format(base_fixture['eps']['h1']['mac'], UNKNOWN_MAC, UNKNOWN_IP,\
            base_fixture['eps']['h1']['ip'])
    helper.do_run_scapy_cmd('h1', scapy_cmd)
    time.sleep(STATS_TIMER_DELAY)
    newDropCount = helper.get_table_drop_counter(7)
    newPromDropCount = helper.get_prometheus_table_drop_counter('ROUTE_TABLE')
    assert((currDropCount+1)==newDropCount)
    assert((currPromDropCount+1)==newPromDropCount)

def test_policy_table_drop(base_fixture):
    ep_list =[{'name': 'h4', 'virt_router_ip': '11.0.0.1', 'ip': '11.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group4'},
              {'name': 'h5', 'virt_router_ip': '12.0.0.1', 'ip': '12.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group5'}
             ]
    helper.create_ep(ep_list, base_fixture)
    currDropCount = helper.get_table_drop_counter(12)
    currPromDropCount = helper.get_prometheus_table_drop_counter('POL_TABLE')
    helper.do_ping_ep(base_fixture,'h4','h5', expectFailure=True)
    time.sleep(STATS_TIMER_DELAY)
    newDropCount = helper.get_table_drop_counter(12)
    newPromDropCount = helper.get_prometheus_table_drop_counter('POL_TABLE')
    assert((currDropCount+1)==newDropCount)
    assert((currPromDropCount+1)==newPromDropCount)

# Send a packet with incorrect vlan tag
def test_group_map_table_drop(base_fixture):
    ep_list =[{'name': 'h4', 'virt_router_ip': '11.0.0.1', 'ip': '11.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group4'}
             ]
    helper.create_ep(ep_list, base_fixture)
    currDropCount = helper.get_table_drop_counter(1,'br-access')
    currPromDropCount = helper.get_prometheus_table_drop_counter('GROUP_MAP_TABLE','br-access')
    helper.do_run_scapy_cmd('h4', "sendp(Ether(dst=\"ff:ff:ff:ff:ff:ff\")/Dot1Q(vlan=100))")
    time.sleep(STATS_TIMER_DELAY)
    newDropCount = helper.get_table_drop_counter(1,'br-access')
    newPromDropCount = helper.get_prometheus_table_drop_counter('GROUP_MAP_TABLE','br-access')
    assert((currDropCount+1)==newDropCount)
    assert((currPromDropCount+1)==newPromDropCount)

# Send a packet which fails ingress security group policy
def test_sec_group_in_table_drop(base_fixture):
    ep_list =[{'name': 'h1', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1'},\
              {'name': 'h8', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.100',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1',\
               'sec_grps': [{"policy-space": "test", "name": "secGrp1"}]
               }
             ]
    helper.create_ep(ep_list, base_fixture)
    currDropCount = helper.get_table_drop_counter(2,'br-access')
    currPromDropCount = helper.get_prometheus_table_drop_counter('SEC_GROUP_IN_TABLE','br-access')
    scapy_cmd = "send(IP(dst=\"{}\")/UDP(sport=30000,dport=50000))".\
            format(base_fixture['eps']['h8']['ip'])
    helper.do_run_scapy_cmd('h1', scapy_cmd)
    time.sleep(STATS_TIMER_DELAY)
    newDropCount = helper.get_table_drop_counter(2,'br-access')
    newPromDropCount = helper.get_prometheus_table_drop_counter('SEC_GROUP_IN_TABLE','br-access')
    assert((currDropCount+1)==newDropCount)
    assert((currPromDropCount+1)==newPromDropCount)

# Send a packet which fails egress security group policy
# h8 allows only ARP  and ICMP
def test_sec_group_out_table_drop(base_fixture):
    ep_list =[{'name': 'h1', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.4',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1'},\
              {'name': 'h8', 'virt_router_ip': '10.0.0.128', 'ip': '10.0.0.100',\
               'prefix_len': 24, 'policy_space_name': 'test', 'epg': 'group1',\
               'sec_grps': [{"policy-space": "test", "name": "secGrp1"}]
               }
             ]
    helper.create_ep(ep_list, base_fixture)
    currDropCount = helper.get_table_drop_counter(3,'br-access')
    currPromDropCount = helper.get_prometheus_table_drop_counter('SEC_GROUP_OUT_TABLE','br-access')
    scapy_cmd = "send(IP(dst=\"{}\")/UDP(sport=30000,dport=50000))".\
            format(base_fixture['eps']['h1']['ip'])
    helper.do_run_scapy_cmd('h8', "send(IP(dst=\"10.0.0.4\")/UDP(sport=30000,dport=50000))")
    time.sleep(STATS_TIMER_DELAY)
    newDropCount = helper.get_table_drop_counter(3,'br-access')
    newPromDropCount = helper.get_prometheus_table_drop_counter('SEC_GROUP_OUT_TABLE','br-access')
    assert((currDropCount+1)==newDropCount)
    assert((currPromDropCount+1)==newPromDropCount)

