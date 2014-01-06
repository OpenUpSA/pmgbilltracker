"""
Scrapes committee reports from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
from dateutil import parser as date_parser
from datetime import datetime
import scrapertools
import simplejson
import re


class ReportPager(object):
    def __init__(self, start_url):
        self.current_url = start_url
        self.current_page = scrapertools.URLFetcher(self.current_url).html

    @property
    def next_page(self):
        soup = BeautifulSoup(self.current_page)
        reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
        next_link = reports_tab.find("li", {"class": "pager-next"})
        if next_link:
            href = "http://www.pmg.org.za" + next_link.find('a').attrs[0][1]
            self.current_url = href
            self.current_page = scrapertools.URLFetcher(self.current_url).html
            return True
        return False

    @property
    def next_report(self):

        keep_going = True
        while keep_going:
            soup = BeautifulSoup(self.current_page)
            reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
            if reports_tab is None:
                print("No reports tab for this committee.")
                print(self.current_url)
                break
            table_body = reports_tab.find("tbody")
            if not self.next_page:
                keep_going = False
            if table_body:
                rows = table_body.findAll("tr")
                for row in rows:
                    try:
                        cells = row.findAll('td')
                        date = date_parser.parse(cells[1].find('span').contents[0]).date()
                        title = cells[2].find('a').contents[0]
                        href = "http://www.pmg.org.za" + cells[2].find('a').attrs[0][1]
                        yield date, title, href
                    except Exception:
                        print("Error reading committee report details from table row")
                        pass


def run_scraper(DEBUG, committee_url, location=None):

    count = 0
    report_list = []
    report_pager = ReportPager(committee_url)
    for (j, (date, title, href_report)) in enumerate(report_pager.next_report):
        if DEBUG:
            print("\t\t" + str(date) + " - " + title)
        tmp_url = href_report
        html = scrapertools.URLFetcher(tmp_url).html
        bills = scrapertools.find_bills(html)
        if bills:
            count += 1
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
            report_list.append(entry)
    return report_list


if __name__ == "__main__":

    DEBUG = True
    tmp = [
        "http://www.pmg.org.za/committees/Ad Hoc Committee on Protection of State Information Bill (NA)",
        "http://www.pmg.org.za/committees/Reparation Committee",
        "http://www.pmg.org.za/committees/committees/Ad Hoc Committee on Protection of State Information Bill (NCOP)",
    ]
    for url in tmp:
        reports = run_scraper(DEBUG, url)


