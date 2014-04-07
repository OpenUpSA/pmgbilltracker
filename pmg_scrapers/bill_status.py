"""
Scrapes committees from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup, Tag

import scrapertools
from pmg_scrapers import logger
from pmg_backend.models import *
from pmg_backend import db
import json


class StatusScraper(object):

    def __init__(self):
        self.bill_status = {}
        self.stats = {
            "total_committees": 0,
            "new_committees": 0,
            "errors": []
        }

    def run_scraper(self):
        """
        Iterate through the bill status pages in /data
        """

        html = open('/Users/petrus/Desktop/code4sa/pmgbilltracker/data/bill_status_2007.html', 'r').read()
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        # container = soup.find(id="committees-all")
        status_tables = soup.findAll("table", {"class": "MsoNormalTable"})
        for status_table in status_tables:
            rows = status_table.findAll("tr")
            # loop through table rows, skipping the header
            for row in rows[1::]:
                cells = row.findAll('td')
                tmp_row = []
                for i in range(len(cells)):
                    cell = cells[i]
                    tmp_cell = ""
                    content_list = cell.findAll("p")
                    for item in content_list:
                        for tag in item.recursiveChildGenerator():
                            if isinstance(tag, Tag):
                                content = tag.string
                            else:
                                content = tag
                            if content:
                                tmp_cell += content.encode('ascii', 'replace') + "\n"
                    tmp_cell = tmp_cell[0:-1]
                    tmp_row.append(tmp_cell)
                print(tmp_row)
        return




if __name__ == "__main__":

    status_scraper = StatusScraper()
    status_scraper.run_scraper()
    logger.info(json.dumps(status_scraper.stats, indent=4))
