#!/usr/bin/python3

import json
import re
import sys
import time
import argparse


def get_address(fileName):
    with open(fileName,'r') as fd:
        a = json.load(fd)
        return a["ip"][0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get the first IP address of an EP given the ep file')
    parser.add_argument('ep_file', metavar='ep_file', help='Ep file name with path')
    args = parser.parse_args()
    print(get_address(args.ep_file))
