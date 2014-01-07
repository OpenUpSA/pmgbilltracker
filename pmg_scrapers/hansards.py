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


class HansardPager(object):
    def __init__(self, DEBUG):
        self.DEBUG = DEBUG
        self.current_url = "http://www.pmg.org.za/hansard"
        self.current_page = scrapertools.URLFetcher(self.current_url).html

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
        keep_going = True
        while keep_going:
            soup = BeautifulSoup(self.current_page)
            hansards_table = soup.find("table", {"class": "views-table cols-2"})
            if hansards_table is None:
                print("No hansards table for this page.")
                print(self.current_url)
                break
            table_body = hansards_table.find("tbody")
            if not self.next_page:
                keep_going = False
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
                        print("Error reading hansard details from table row.")
                        pass


def run_scraper(DEBUG):

    count = 0
    hansard_list = []
    hansard_pager = HansardPager(DEBUG)
    for (j, (date, title, href_hansard)) in enumerate(hansard_pager.next_hansard):
        if DEBUG:
            print("\t\t" + str(date) + " - " + title)
        time.sleep(0.5)
        tmp_url = href_hansard
        html = scrapertools.URLFetcher(tmp_url).html
        soup = BeautifulSoup(html)
        content = soup.find(id="content")
        bills = scrapertools.find_bills(str(content))
        if bills:
            count += 1
            # infer location from title
            # TODO: convince them to make this check easier, because many entries won't be tagged correctly
            location = None
            if title.startswith("NA:"):
                location = 1
            elif title.startswith("NCOP:"):
                location = 2
            entry = {
                "bills": bills,
                "url": tmp_url,
                "date": date,
                "title": title,
                "location": location
                }
            if DEBUG:
                print("\t\t\tentry #" + str(count) + " - " + str(bills))
                print(simplejson.dumps(entry, indent=4, default=scrapertools.handler))
            hansard_list.append(entry)
    return hansard_list


if __name__ == "__main__":

    DEBUG = True
    hansards = run_scraper(DEBUG)


