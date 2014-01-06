"""
Scrapes committees from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
# from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from datetime import datetime
from pmg_scrapers import scrapertools
import simplejson
import re


class CommitteePager(object):

    def __init__(self, DEBUG):
        self.DEBUG = DEBUG

    @property
    def next_committee(self):
        html = scrapertools.URLFetcher("http://www.pmg.org.za/committees").html
        soup = BeautifulSoup(html)
        container = soup.find(id="committees-all")
        committee_lists = container.findAll("div", {"class": "item-list"})
        for committee_list in committee_lists:
            list_name = committee_list.find('h3').contents[0]
            if self.DEBUG:
                print("\n" + list_name + ":")
            committees = committee_list.findAll('li')
            for committee in committees:
                href = "http://www.pmg.org.za" + committee.find('a').attrs[0][1]
                name = committee.find('a').contents[0]
                if self.DEBUG:
                    print("\t" + name)
                yield list_name, href, name


def run_scraper(DEBUG):

    committee_pager = CommitteePager(DEBUG)
    committees = []

    for (i, (list_name, href_committee, name)) in enumerate(committee_pager.next_committee):
        tmp = {
            "type": list_name,
            "url": href_committee,
            "name": name
        }
        committees.append(tmp)
    return committees


if __name__ == "__main__":

    DEBUG = True
    run_scraper(DEBUG)
