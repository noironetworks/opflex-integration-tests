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
from opflex_integration_tests import utils
import os
import pytest
import re
import sys
import time
from contextlib import contextmanager 

#@contextmanager
#def opflex_ep_test_context(*args, **kwds):



def ep_netns(ep):
    return "/var/run/netns/{0}".format(ep)

def do_ping_ep(ep_store, ep, expectFailure=False):
    host = ""
    if ep in ep_store:
        host = ep_store[ep]['ip']
    else:
        return
    cmdString = "/usr/bin/ping {0} -c 1 -W 1".format(host[0])
    utils.execute(cmdString, expectFailure)

def get_table_drop_counter(tableId, bridge='br-int'):
    cmdString = "\"gbp_inspect -fprq GbpeTableDropCounter | grep -A 4 \'{0}/{1}\'\"".format(bridge, tableId)
    gbpOut = utils.execute(cmdString, runWithShell=True)
    gbpOutStr = str(gbpOut)
    m = re.search('packets(\\s*):(\\s*)([0-9]+)', gbpOutStr)
    return int(m.group(3))

