import pytest
from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_PATH = os.path.abspath('tests/templates')
GEN_TEST_DIR = '/tmp/gen_test_data'
env = Environment(loader=FileSystemLoader(TEMPLATE_PATH),
                  trim_blocks=True,
                  lstrip_blocks=True)
