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
from tests import helper
from dynaconf import settings

STATS_TIMER_DELAY = settings.STATS_TIMER_DELAY

@pytest.mark.skip(reason="Still working on this")
def test_security_table_drop():
    with open('/proc/self/ns/net', 'r') as fd, \
    open(helper.ep_netns('h4'), 'r') as ns_fd:
        netns.setns(ns_fd)
        currDropCount = helper.get_table_drop_counter(1)
        utils.execute('/usr/bin/ping 12.0.0.4 -c 1 -W 1', expectFailure=True)
        newDropCount = helper.get_table_drop_counter(1)
        assert((currDropCount+1)==newDropCount)
        netns.setns(fd)

def test_policy_table_drop(ep_store):
    with open('/proc/self/ns/net', 'r') as fd, \
    open(helper.ep_netns('h4'), 'r') as ns_fd:
        netns.setns(ns_fd)
        currDropCount = helper.get_table_drop_counter(12)
        helper.do_ping_ep(ep_store, 'h5', expectFailure=True)
        time.sleep(STATS_TIMER_DELAY)
        newDropCount = helper.get_table_drop_counter(12)
        assert((currDropCount+1)==newDropCount)
        netns.setns(fd)

