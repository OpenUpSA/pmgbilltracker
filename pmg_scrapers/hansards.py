"""
Scrapes hansards from PMG e.g.
http://www.pmg.org.za/hansard
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
from dateutil import parser as date_parser
import scrapertools
import simplejson
import time
from pmg_scrapers import logger
from pmg_backend.models import *
from pmg_backend import db
import json


class HansardScraper(object):

    def __init__(self):
        self.current_url = "http://www.pmg.org.za/hansard"
        self.current_page = scrapertools.URLFetcher(self.current_url).html
        self.current_hansard = {}
        self.stats = {
            "total_hansards": 0,
            "new_hansards": 0,
            "errors": []
        }

    @property
    def next_page(self):

        soup = BeautifulSoup(self.current_page)
        next_link = soup.find("li", {"class": "pager-next"})
        if next_link:
            href = "http://www.pmg.org.za" + next_link.find('a').attrs[0][1]
            self.current_url = href
            self.current_page = scrapertools.URLFetcher(self.current_url).html
            return True
        return False

    @property
    def next_hansard(self):

        soup = BeautifulSoup(self.current_page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        hansards_table = soup.find("table", {"class": "views-table cols-2"})
        if hansards_table is None:
            self.stats["errors"].append("No hansards table for this page: " + self.current_url)
            raise ValueError
        table_body = hansards_table.find("tbody")

        if table_body:
            rows = table_body.findAll("tr")
            for row in rows:
                cells = row.findAll('td')
                try:
                    date = date_parser.parse(cells[0].find('span').contents[0]).date()
                    title = cells[1].find('a').contents[0]
                    href = "http://www.pmg.org.za" + cells[1].find('a').attrs[0][1]
                    yield date, title, href
                except Exception:
                    self.stats["errors"].append("Error reading hansard details from table row.")
                    pass

    def run_scraper(self):

        while True:
            for (j, (date, title, href_hansard)) in enumerate(self.next_hansard):
                logger.debug("\t\t" + str(date) + " - " + title)
                time.sleep(0.25)
                tmp_url = href_hansard
                html = scrapertools.URLFetcher(tmp_url).html
                soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
                content = soup.find(id="content")
                # find bills that are mentioned in the text
                bills = scrapertools.find_bills(str(content))
                # only save hansards that are related to bills
                if bills:
                    # infer location from title
                    # TODO: convince them to make this check easier, because many entries won't be tagged correctly
                    location = None
                    if title.startswith("NA:"):
                        location = 1
                    elif title.startswith("NCOP:"):
                        location = 2
                    self.current_hansard = {
                        "bills": bills,
                        "url": tmp_url,
                        "date": date,
                        "title": title,
                        "location": location
                    }
                    logger.debug(simplejson.dumps(self.current_hansard, indent=4, default=scrapertools.handler))
                    try:
                        self.add_or_update()
                    except Exception:
                        msg = "Could not add hansard to database: "
                        if self.current_hansard.get("title"):
                            msg += self.current_hansard["title"]
                        self.stats["errors"].append(msg)
                        logger.error(msg)
                    self.current_hansard = {}

            # save hansards to database, once per scraped page
            db.session.commit()
            # test whether we have reached the end
            if not self.next_page:
                break
        return

    def add_or_update(self):
        """
        Add current_hansard to database, or update the record if it already exists.
        """

        self.current_hansard['entry_type'] = "hansard"
        bills = []
        if self.current_hansard.get('bills'):
            bills = self.current_hansard["bills"]
            # TODO: improve filtering
        hansard = Entry.query.filter(Entry.type=="hansard").filter(Entry.title==self.current_hansard['title']).first()
        if hansard is None:
            hansard = Entry()
            self.stats["new_hansards"] += 1
        hansard = scrapertools.populate_entry(hansard, self.current_hansard, bills)
        db.session.add(hansard)
        self.stats["total_hansards"] += 1
        return


if __name__ == "__main__":

    hansard_scraper = HansardScraper()
    hansard_scraper.run_scraper()
    logger.info(json.dumps(hansard_scraper.stats, indent=4))


