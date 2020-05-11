import logging
import os
from logging.config import fileConfig

def get_logger(name):
    filepath = os.path.abspath('config/logging.ini')
    fileConfig(filepath, disable_existing_loggers=False)
    log = logging.getLogger(name)
    return log

