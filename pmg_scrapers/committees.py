"""
Scrapes committees from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
# from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from datetime import datetime
import scrapertools
import simplejson
import re
from pmg_scrapers import logger


class CommitteePager(object):

    @property
    def next_committee(self):
        html = scrapertools.URLFetcher("http://www.pmg.org.za/committees").html
        soup = BeautifulSoup(html)
        container = soup.find(id="committees-all")
        committee_lists = container.findAll("div", {"class": "item-list"})
        for committee_list in committee_lists:
            list_name = committee_list.find('h3').contents[0]
            logger.debug("\n" + list_name + ":")
            committees = committee_list.findAll('li')
            for committee in committees:
                href = "http://www.pmg.org.za" + committee.find('a').attrs[0][1]
                name = committee.find('a').contents[0]
                logger.debug("\t" + name)
                yield list_name, href, name


def run_scraper():

    committee_pager = CommitteePager()
    committees = []

    for (i, (list_name, href_committee, name)) in enumerate(committee_pager.next_committee):
        # determine committee's location
        location = None
        if list_name == "National Assembly Committees":
            location = 1
        elif list_name == "NCOP Committees":
            location = 2
        elif list_name == "Joint Committees":
            location = 3
        else:
            if "(NA)" in name:
                location = 1
            elif "(NCOP)" in name:
                location = 2
        # populate entry
        tmp = {
            "type": "committee",
            "url": href_committee,
            "name": name,
            "location": location
        }
        committees.append(tmp)
    return committees


if __name__ == "__main__":

    run_scraper()
