"""
Scrapes all bills introduced from 2006 until now from PMG e.g.
www.pmg.org.za/bill?year=2013, while including links to bill versions and the introduction date
"""
from __future__ import print_function
import json
from BeautifulSoup import BeautifulSoup
from dateutil import parser as date_parser
from datetime import datetime
import scrapertools
from pmg_scrapers import logger
from pmg_backend.models import *
from pmg_backend import db


class BillScraper(object):
    """
    State machine for extracting a list of bills from an html table. It operates on a list of table rows, extracting
    one bill at a time.

    The calling function should keep calling the method stored in 'state_fn', which will return True once it is
    finished parsing a particular row.

    Bills look like:
    <tr class="odd"><td colspan="2"><strong>Bill 30 - Marine Living Resources Amendment Bill</strong></td> </tr>
    <tr class="even"><td>&nbsp;&nbsp;&nbsp;&nbsp;<a href="/bill/20131029-marine-living-resources-amendment-bill-b30b-2013">B30B-2013</a></td><td>29 Oct, 2013</td> </tr>
    """
    def __init__(self, session):
        self.session = session
        self.state_fn = self.start_state
        self.current_bill = {}
        self.stats = {
            "total_bills": 0,
            "total_bill_versions": 0,
            "total_drafts": 0,
            "new_bills": 0,
            "new_bill_versions": 0,
            "new_drafts": 0,
            "errors": []
        }

    def run_scraper(self):
        """
        Iterate through bill pages, and run the state machine for each page.
        """
        pager = Pager()

        # iterate through bill pages
        for url in pager.next_page:
            logger.info(url)

            # initiate parser for this page
            self.state_fn = self.start_state
            html = scrapertools.URLFetcher(url, self.session).html
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            rows = soup.findAll("tr")

            # feed rows into state machine
            for row in rows:
                while not self.state_fn(row):
                    pass
            # commit to database after each page
            # db.session.commit()
        return

    def add_or_update(self):
        """
        Add current_bill to database, or update the record if it already exists.
        Then clear the current_bill attribute to make it ready for the next bill to be scraped.
        """

        # TODO: clean up the Draft vs. Bill logic below
        # TODO: check that the numbers add up correctly
        bill_data = self.current_bill

        try:
            if self.current_bill.get('status') and self.current_bill['status'] == "Draft":
                # save scraped draft bill to database
                bill = Bill.query.filter(Bill.name==bill_data['bill_name']).filter(Bill.year==bill_data['year']).first()
                if bill is None:
                    bill = Bill()
                    bill.name = bill_data['bill_name']
                    bill.year = bill_data['year']
                    self.stats['new_drafts'] += 1
                bill.bill_type = "Draft"
                db.session.add(bill)
                self.stats['total_drafts'] += 1

            else:
                # save scraped bills to database
                bill_code = self.current_bill["code"]
                bill = Bill.query.filter(Bill.code==bill_code).first()
                if bill is None:
                    bill = Bill()
                    bill.code = bill_code
                    self.stats['new_bills'] += 1
                bill.name = bill_data['bill_name']
                bill.year = bill_data['year']
                bill.number = bill_data['number']
                db.session.add(bill)
                self.stats['total_bills'] += 1

            # save related bill versions
            for entry_data in bill_data['versions']:
                entry = Entry.query.filter(Entry.url==entry_data['url']).first()  # Look for pre-existing entry.
                if entry is None:
                    entry = Entry()  # Create new entry.
                    self.stats['new_bill_versions'] += 1
                entry = scrapertools.populate_entry(entry, entry_data)
                entry.bills.append(bill)
                db.session.add(entry)
                self.stats['total_bill_versions'] += 1

        except Exception:
            error_msg = "Error saving bill: "
            if self.current_bill.get('bill_name'):
                error_msg += self.current_bill['bill_name']
            if self.current_bill.get('versions'):
                error_msg += " - " + self.current_bill['versions'][0]['title']
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            pass

        logger.debug(json.dumps(self.current_bill, indent=4, default=scrapertools.handler))
        self.current_bill = {}
        return

    def start_state(self, fragment):
        """
        Inititialize State Machine for a particular page.
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

        if self.current_bill:
            # save previously scraped bill
            self.add_or_update()
            # commit to database
            db.session.commit()
            

        text = fragment.text
        parts = text.split("-")
        tmp = "-".join(parts[1::]).strip()  # disregards the bill number, just use the rest of the text
        if "[" in tmp and "]" in tmp:
            tmp = tmp[0:tmp.find("[")].strip()  # throw away extracted info
        self.current_bill["bill_name"] = tmp

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
            if not self.current_bill.get("code"):
                tmp = link.text
                info = scrapertools.analyze_bill_code(tmp)
                if info:
                    self.current_bill = dict(self.current_bill.items() + info.items())
                else:
                    logger.error("No bill found in string: " + tmp)

            version = {
                "url": link["href"],
                "title": link.text,
                "date": date_parser.parse(fragment.findAll("td")[1].text).date(),
                "entry_type": "bill-version",
                }
            # set entry_type appropriately if this bill has already been enacted
            if "as enacted" in link.text:
                version['entry_type'] = "act"
            versions.append(version)
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
        current_year = datetime.today().year
        for current_year in range(current_year, 2005, -1):
            url = "http://www.pmg.org.za/print/bill?year=%d" % current_year
            yield url


if __name__ == "__main__":

    bill_scraper = BillScraper()
    bill_scraper.run_scraper()
    logger.info(json.dumps(bill_scraper.stats, indent=4))
