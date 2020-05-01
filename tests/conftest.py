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
import glob
import json
import logging
from opflex_integration_tests import utils
import os
import pytest
import re
import sys
import time

@pytest.fixture(scope="module")
def ep_store():
    ep_config = {}
    for f in glob.glob('config/*.ep'):
        m = re.search('config\/(.*)\.ep',f)
        if m is None:
            continue
        with open(f,'r') as fd:
            a = json.load(fd)
            ep_config[m.group(1)] = a
    return ep_config

