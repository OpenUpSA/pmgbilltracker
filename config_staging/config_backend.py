import os.path as op
import logging

HOST = 'billsapi.pmg.org.za'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/pmgbilltracker.db'

LOG_LEVEL = logging.INFO
LOGGER_NAME = "pmg_backend_logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = False

SECRET_KEY = "AEORJAAEGIAJEGPKAEGGOAERGN"