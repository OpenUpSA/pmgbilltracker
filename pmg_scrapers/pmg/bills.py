"""
Scrapes all bills introduced from 2006 until now from PMG e.g.
www.pmg.org.za/bill?year=2013, while including links to bill versions and the introduction date
"""
from __future__ import print_function
import sys
import json
from BeautifulSoup import BeautifulSoup
from dateutil import parser as date_parser
from datetime import datetime
import pmg_scrapers.scrapertools

DEBUG = False

class BillParser(object):
    """
    State machine for extracting a list of bills from an html table. It operates on a list of table rows, extracting
    one bill at a time.

    The calling function should keep calling the method stored in 'state_fn', which will return True once it is
    finished parsing a particular row.

    Bills look like:
    <tr class="odd"><td colspan="2"><strong>Bill 30 - Marine Living Resources Amendment Bill</strong></td> </tr>
    <tr class="even"><td>&nbsp;&nbsp;&nbsp;&nbsp;<a href="/bill/20131029-marine-living-resources-amendment-bill-b30b-2013">B30B-2013</a></td><td>29 Oct, 2013</td> </tr>
    """
    def __init__(self):
        self.state_fn = self.start_state
        self.bills = []
        self.current_bill = {}

    def start_state(self, fragment):
        """
        Inititialize State Machine
        """
        if not fragment.find("strong"):
            return True

        self.state_fn = self.header_state
        return False

    def header_state(self, fragment):
        """
        Extract info from header row.
        """
        if not fragment.find("strong"):
            raise Exception("Unknown state")

        self.bills.append(self.current_bill)

        text = fragment.text

        text = text.replace(u"\u2013", "-")  # TODO: do this for all years
        parts = text.split("-")
        self.current_bill["bill_number"] = parts[0].strip()
        self.current_bill["bill_name"] = parts[1].strip()
        if len(parts) == 3:
            self.current_bill["introduced_by"] = parts[2].strip()
        if DEBUG:
            print(text)
            print("\tbill_number: " + self.current_bill["bill_number"])
            print("\tbill_name: " + self.current_bill["bill_name"])
            try:
                print("\tintroduced_by: " + self.current_bill["introduced_by"])
            except KeyError:
                pass

        self.state_fn = self.version_state
        return True

    def version_state(self, fragment):
        """
        Extract available versions from second row.
        """
        link = fragment.find("a")
        if link: 
            versions = self.current_bill.setdefault("versions", [])
            url = link["href"]
            versions.append({
                "url" : link["href"],
                "name" : link.text,
                "date" : date_parser.parse(fragment.findAll("td")[1].text).date(),
            })
            self.state_fn = self.version_state
            return True
        else:
            self.state_fn = self.header_state
            return False


class Pager(object):
    """
    Return an iterable containing URLs to each of the available bills pages.
    """
    @property
    def next_page(self):
        if DEBUG:
            yield "http://www.pmg.org.za/print/bill?year=2013"
        else:
            current_year = datetime.today().year
            for current_year in range(current_year, 2005, -1):
                url = "http://www.pmg.org.za/print/bill?year=%d" % current_year
                yield url


if __name__ == "__main__":

    DEBUG = True

    pager = Pager()
    bills = []

    # iterate through bill pages
    for url in pager.next_page:
        print(url, file=sys.stderr)

        # initiate parser for this page
        parser = BillParser()
        html = pmg_scrapers.scrapertools.URLFetcher(url).html
        soup = BeautifulSoup(html)
        rows = soup.findAll("tr")

        # feed rows into state machine
        for row in rows:
            while not parser.state_fn(row):
                pass

        # save extracted content for this page
        bills.extend(parser.bills)

    if not DEBUG:
        # do something with scraped data
        print(json.dumps(bills, indent=4, default=pmg_scrapers.scrapertools.handler))
