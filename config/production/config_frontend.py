import os.path as op
import logging

HOST = 'bills.pmg.org.za'
# API_HOST = 'billsapi.pmg.org.za'
API_HOST = '0.0.0.0:5001'

LOG_LEVEL = logging.INFO
LOGGER_NAME = "pmg_backend_logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = False