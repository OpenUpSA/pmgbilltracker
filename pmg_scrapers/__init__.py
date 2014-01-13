import logging

logging.basicConfig(filename="debug.log",
                    filemode='w',
                    format='%(asctime)s, %(levelname)s [%(name)s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger("pmg_scraper")