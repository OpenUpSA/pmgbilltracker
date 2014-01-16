"""
Scrapes committees from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
import scrapertools
from pmg_scrapers import logger
from pmg_backend.models import *
from pmg_backend import db
import json


class CommitteeScraper(object):

    def __init__(self):
        self.current_committee = {}
        self.stats = {
            "total_committees": 0,
            "new_committees": 0,
            "errors": []
        }

    def run_scraper(self):
        """
        Iterate through committees on http://www.pmg.org.za/committees, and scrape their details.
        """

        for (i, (list_name, href_committee, name)) in enumerate(self.next_committee):
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
            self.current_committee = {
                "type": "committee",
                "url": href_committee,
                "name": name,
                "location": location
            }
            try:
                self.add_or_update()
            except Exception:
                msg = "Could not add committee to database: "
                if self.current_committee.get("name"):
                    msg += self.current_committee["name"]
                self.stats["errors"].append(msg)
                logger.error(msg)
                self.current_committee = {}
        db.session.commit()
        return

    def add_or_update(self):
        """
        Add current_committee to database, or update the record if it already exists. Then clear the attribute.
        """

        agent = Agent.query.filter(Agent.name==self.current_committee['name'])\
            .filter(Agent.type==self.current_committee['type']).first()
        if agent is None:
            agent = Agent()
            agent.name = self.current_committee['name']
            agent.type = self.current_committee['type']
            agent.location = self.current_committee['location']
            self.stats["new_committees"] += 1
        agent.url = self.current_committee['url']
        db.session.add(agent)
        self.stats["total_committees"] += 1
        self.current_committee = {}
        return

    @property
    def next_committee(self):
        html = scrapertools.URLFetcher("http://www.pmg.org.za/committees").html
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
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


if __name__ == "__main__":

    committee_scraper = CommitteeScraper()
    committee_scraper.run_scraper()
    logger.info(json.dumps(committee_scraper.stats, indent=4))
