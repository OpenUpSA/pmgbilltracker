import logging
import sys

file_handler = logging.FileHandler(filename="scraper.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
formatter_min = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')

logger = logging.getLogger("pmg_scraper")
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

