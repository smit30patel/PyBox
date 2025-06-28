import sys
import os

module_dir = os.path.abspath('../common')
sys.path.append(module_dir)

from logger import setup_logger

logger = setup_logger('PyBox/client/client_logger.py')
# logger.warning("This is a test log message.")