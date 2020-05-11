#!/usr/bin/python3
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
import pytest
import shlex
import subprocess
import sys
import time
from dynaconf import settings
from opflex_integration_tests import logger

LOG=logger.get_logger(__name__)
EXEC_TIMEOUT = settings.EXEC_TIMEOUT


def execute(cmdline, expectFailure=False, runWithShell=False):
    cmd = shlex.split(cmdline)
    if runWithShell:
        cmd_output = subprocess.Popen(cmd, shell=True,
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE)
    else:
        cmd_output = subprocess.Popen(cmd,
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE)
    output, err = cmd_output.communicate(timeout=EXEC_TIMEOUT)
    if err != b'':
        LOG.error("%s" % err)
    if not expectFailure:
        if cmd_output.returncode != 0:
            LOG.error("%s" % output)
        assert(cmd_output.returncode == 0)
    else:
        assert(cmd_output.returncode != 0)
    return output
