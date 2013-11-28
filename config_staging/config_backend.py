import os.path as op
import logging

HOST = 'api.demo4sa.org'
SQLALCHEMY_DATABASE_URI = 'sqlite:///pmgbilltracker.db'

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "pmg_backend_logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SECRET_KEY = "AEORJAEONIAEGCBGKMALMAENFXGOAERGN"

UPLOAD_PATH = op.join(op.dirname(__file__), 'uploads')