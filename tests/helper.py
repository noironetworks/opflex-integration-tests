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
from opflex_integration_tests import utils
from tests.template_utils import env
import os
import pytest
import re
import sys
import time
from pyroute2 import netns
from contextlib import contextmanager 
import logging
import shlex
import uuid
import json
from dynaconf import settings
import pdb

EP_FILE_PATH = settings.EP_FILE_PATH

LOG = logging.getLogger(__name__)

def do_run_scapy_cmd(ep1, cmd):
    cmdString = "ip netns exec {} tests/run_scapy_cmd.py {}".format(ep1, shlex.quote(cmd))
    utils.execute(cmdString)

def do_ping_ep(test_ctxt, ep1, ep2, expectFailure=False):
    host = test_ctxt['eps'][ep2]['ip']
    cmdString = "ip netns exec {} /usr/bin/ping {} -c 1 -W 2".format(ep1, host)
    utils.execute(cmdString, expectFailure)

def get_table_drop_counter(tableId, bridge='br-int'):
    cmdString = "\"gbp_inspect -fprq GbpeTableDropCounter | grep -A 4 \'{0}/{1}/\'\"".format(bridge, tableId)
    gbpOut = utils.execute(cmdString, runWithShell=True)
    gbpOutStr = str(gbpOut)
    m = re.search('packets(\\s*):(\\s*)([0-9]+)', gbpOutStr)
    return int(m.group(3))

def get_prometheus_table_drop_counter(tableName, bridge='br-int'):
    cmdString = "\"curl --compressed --silent http://127.0.0.1:9612/metrics 2>&1| grep {0}_{1}\"".format(bridge, tableName)
    gbpOut = utils.execute(cmdString, runWithShell=True)
    gbpOutStr = str(gbpOut)
    searchStr = "opflex_table_drop_packets{{table=\"{0}_{1}\"}} ([0-9]+).0.*".format(bridge, tableName)
    m = re.search(searchStr, gbpOutStr)
    return int(m.group(1))

def setup_ep(ep):
    cmdString = "ip netns add {}".format(ep['name'])
    utils.execute(cmdString)
    veth_ends = [ep['name']+"veth", ep['name']+"eth"]
    cmdString = "ip link add name {} type veth peer name {}".\
            format(veth_ends[0], veth_ends[1])
    utils.execute(cmdString)
    cmdString = "ip link set dev {} up netns {}".\
            format(veth_ends[0], ep['name'])
    utils.execute(cmdString)
    cmdString = "ip netns exec {} ifconfig lo up".\
            format(ep['name'])
    utils.execute(cmdString)
    cmdString = "ifconfig {} up".format(veth_ends[1])
    utils.execute(cmdString)
    cmdString = "ip netns exec {} ip addr add {} dev {}".\
            format(ep['name'], ep['ip']+'/'+str(ep['prefix_len']),
                    veth_ends[0])
    utils.execute(cmdString)
    cmdString = "ip netns exec {} ip route add 0.0.0.0/0 via {}".\
            format(ep['name'], ep['virt_router_ip'])
    utils.execute(cmdString)
    if 'disable_ipv6' in ep:
        if ep['disable_ipv6']:
            cmdString = "ip netns exec {} sysctl -w net.ipv6.conf.{}.disable_ipv6=1".\
                    format(ep['name'], veth_ends[0])
            utils.execute(cmdString)
    cmdString = "ovs-vsctl add-port br-access {}".format(veth_ends[1])
    utils.execute(cmdString)
    cmdString = "ovs-vsctl -- add-port br-access qpf-{0}"\
            " -- set interface qpf-{0} type=patch options:peer=qpi-{0}"\
            " -- add-port br-int qpi-{0}"\
            " -- set interface qpi-{0} type=patch options:peer=qpf-{0}".\
            format(veth_ends[1])
    utils.execute(cmdString)

def dump_template(file_name, file_data):
    with open(file_name,'w') as out_file:
        out_file.write(file_data)
        out_file.write("\n")

def create_ep(ep_list, test_ctxt):
    for ep in ep_list:
        setup_ep(ep)
        cmdString = "\"ip netns exec {} ifconfig {} | grep ether\"".\
                format(ep['name'],ep['name']+'veth')
        cmdOut = utils.execute(cmdString,runWithShell=True)
        cmdOutStr = str(cmdOut)
        m = re.search('(\\s*)ether(\\s*)([0-9a-fA-F:]+)', cmdOutStr)
        ep['mac'] = m[3]
        template = env.get_template('temp.ep')
        ep['uuid'] = str(uuid.uuid4())
        ep['acc_int'] = ep['name'] + 'eth'
        file_data = template.render(ep=ep)
        file_name = ep['name'] + '.ep'
        if 'eps' not in test_ctxt:
            test_ctxt['eps'] = {}
        test_ctxt['eps'][ep['name']] = ep
        dump_template(file_name, file_data)
        cmdString = "mv {0} {1}/{0}".format(file_name, EP_FILE_PATH)
        utils.execute(cmdString)

def delete_ep(test_ctxt):
    for ep_name,ep in test_ctxt['eps'].items():
        patch_br_int = "qpi-" + ep['acc_int'] 
        patch_br_access = "qpf-" + ep['acc_int'] 
        cmdString = "ovs-vsctl del-port br-int {}".\
                format(patch_br_int)
        utils.execute(cmdString)
        cmdString = "ovs-vsctl del-port br-access {}".\
                format(patch_br_access)
        utils.execute(cmdString)
        cmdString = "ovs-vsctl del-port br-access {}".format(ep['acc_int'])
        utils.execute(cmdString)
        cmdString = "ip link del {}".format(ep['acc_int'])
        utils.execute(cmdString)
        cmdString = "ip netns del {}".format(ep['name']) 
        utils.execute(cmdString)
        file_name = ep_name + ".ep"
        cmdString = "rm -f {}/{}".format(EP_FILE_PATH,file_name)
        utils.execute(cmdString)

def ep_netns(ep):
    return "/var/run/netns/{0}".format(ep)

@contextmanager
def switch_to_ep(ep):
    try:
        base_ns = open('/proc/self/ns/net','r')
        ep_ns = open(ep_netns(ep), 'r')
        netns.setns(ep_ns)
        yield (base_ns,ep_ns)
    finally:
        netns.setns(base_ns)
        ep_ns.close()
        base_ns.close()

