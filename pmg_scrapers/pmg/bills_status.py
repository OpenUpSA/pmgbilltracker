"""
Scrapes all bill status urls from 2007 from PMG site introduced from 2006 until now from PMG e.g.
www.pmg.org.za/bill?year=2013

Also includes links to bill versions as well as introduction date
"""

from __future__ import print_function
import sys
from datetime import datetime
from BeautifulSoup import BeautifulSoup
import scrapertools
import json


class Pager(object):
    url_pattern = "http://www.pmg.org.za/files/proceedings%d.htm"

    @property
    def next_page(self):
        current_year = datetime.now().year
        for current_year in range(2009, current_year):
            url = Pager.url_pattern % current_year
            yield url

class Parser(object):
    def __init__(self):
        self.bills = []
        self.state_fn = self.initial_state

    def initial_state(self, fragment):
        cells = fragment.findAll("td")
        first_cell = cells[0].text
        if first_cell not in ["Bill", "Act"]:
            raise Exception("Expected table header")

        self.state_fn = self.row_state
        return True

    def row_state(self, fragment):
        cells = fragment.findAll("td")
        values = [" ".join(cell.text.split()) for cell in cells]
        headings = ["Act", "Title", "PC", "NA", "SC", "NCOP", "Passed", "Assent", "Status"]
        if len(values) == 10:
            headings = ["Bill"] + headings
        self.bills.append(dict(zip(headings, values)))
        return True
        
class TableGobbler(object):
    def __init__(self, parser_class):
        self.parser_class = parser_class
        self.bills = []

    def gobble(self, fragment):
        tables = fragment.findAll("table")
        for table in tables:
            parser = self.parser_class()
            for row in table.findAll("tr"):
                while not parser.state_fn(row):
                    pass
            bills.extend(parser.bills) 
        return bills

pager = Pager()

bills = []
for url in pager.next_page:
    print(url, file=sys.stderr)
    parser = Parser()
    html = scrapertools.URLFetcher(url).html
    html = html.decode("windows-1252")
    html = html.replace(u"\u2013", "-")
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    gobbler = TableGobbler(Parser)
    bills = gobbler.gobble(soup)

print(json.dumps(bills, indent=4, default=scrapertools.handler))
