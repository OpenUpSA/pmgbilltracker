"""
Scrapes committee reports from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
from dateutil import parser as dateparser
from datetime import datetime
from pmg_scrapers import scrapertools
import simplejson
import re


class ReportParser(object):
    def __init__(self, report_url):
        self.report_url = report_url
        self.bills = []


class ReportPager(object):
    def __init__(self, start_url):
        self.current_url = start_url
        self.current_page = scrapertools.URLFetcher("http://www.pmg.org.za" + self.current_url).html

    @property
    def next_page(self):
        soup = BeautifulSoup(self.current_page)
        reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
        next_link = reports_tab.find("li", {"class": "pager-next"})
        if next_link:
            href = next_link.find('a').attrs[0][1]
            self.current_url = href
            self.current_page = scrapertools.URLFetcher("http://www.pmg.org.za" + self.current_url).html
            return True
        return False

    @property
    def next_report(self):

        keep_going = True
        while keep_going:
            soup = BeautifulSoup(self.current_page)
            reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
            table_body = reports_tab.find("tbody")
            rows = table_body.findAll("tr")
            if not self.next_page:
                keep_going = False
            for row in rows:
                cells = row.findAll('td')
                date = cells[1].find('span').contents[0]
                title = cells[2].find('a').contents[0]
                href = cells[2].find('a').attrs[0][1]
                yield date, title, href


class CommitteePager(object):
    @property
    def next_committee(self):
        html = scrapertools.URLFetcher("http://www.pmg.org.za/committees").html
        soup = BeautifulSoup(html)
        container = soup.find(id="committees-all")
        committee_lists = container.findAll("div", {"class": "item-list"})
        for committee_list in committee_lists:
            list_name = committee_list.find('h3').contents[0]
            print("\n" + list_name + ":")
            committees = committee_list.findAll('li')
            for committee in committees:
                href = committee.find('a').attrs[0][1]
                name = committee.find('a').contents[0]
                yield list_name, href, name


if __name__ == "__main__":

    count = 0
    committee_pager = CommitteePager()
    for (i, (list_name, href_committee, name)) in enumerate(committee_pager.next_committee):
        print("\t" + str(i+1) + ": " + name)
        report_pager = ReportPager(href_committee)
        for (j, (date, title, href_report)) in enumerate(report_pager.next_report):
            print("\t\t" + date + " - " + title)
            report_parser = ReportParser(href_report)
            html = scrapertools.URLFetcher("http://www.pmg.org.za" + href_report).html
            bills = scrapertools.find_bills(html)
            if bills:
                count += 1
                print("\t\t\tentry #" + str(count) + " - " + str(bills))
                entry = {
                    "bills": bills,
                    "href": href_report,
                    "date": date,
                    "title": title,
                    "location": list_name,
                    "committee": name,
                    }
                print(simplejson.dumps(entry, indent=4))