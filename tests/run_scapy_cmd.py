#!/usr/bin/python3
import argparse
from opflex_integration_tests import logger
import sys
from scapy.all import *

LOG = logger.get_logger(__name__)

def run_scapy_cmd(cmd):
    hit_except = False
    LOG.info("scapy_cmd: %s" % cmd)
    try:
        p = exec(cmd)
    except Exception as e:
        hit_except = True
        LOG.error("%s:%s" % (e,cmd))
    finally:
        if not hit_except:
            return 0
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run scapy non-interactively passing a command')
    parser.add_argument('cmd', help='actual command to run in scapy')
    args = parser.parse_args()
    ret = run_scapy_cmd(args.cmd)
    sys.exit(ret)

