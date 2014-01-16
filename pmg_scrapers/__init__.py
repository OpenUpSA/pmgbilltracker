import logging
import sys
import requests
import json

file_handler = logging.FileHandler(filename="debug.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
formatter_min = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')

logger = logging.getLogger("pmg_scraper")
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

# login and start session with pmg website
logger.info("LOGGING IN")
session = requests.Session()
headers = {'user-agent': 'Mozilla/4.0 (compatible: MSIE 6.0)'}
try:
    config = json.load(open('scraper_config.json'))
    data = {
        'name': config['name'],
        'pass': config['pass'],
        'form_id': 'user_login',
        'form_build_id': 'form-ee72095493d7ed912673b8a83219772c',
        'op': 'Log in'
    }
except Exception:
    logger.error("Configuration Error:")
    logger.error("Please ensure that a file called 'scraper_config.json' exists in the scraper directory, and that it contains" \
          "valid 'username' and 'password' parameters for logging in to the PMG website. This is needed for accessing " \
          "much of the content.")

r = session.post('http://www.pmg.org.za/user/login', headers=headers, data=data)

if not "Welcome back." in r.content:
    logger.error("Login was not successful")
    raise Exception