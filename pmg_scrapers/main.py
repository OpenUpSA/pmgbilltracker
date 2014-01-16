from __future__ import print_function
import datetime
import simplejson
from random import shuffle
import os
import sys
import json

# Add the parent folder path to the sys.path list
path = os.getcwd()
tmp = path.split("/")[0:-1]
parent_path = "/".join(tmp)
sys.path.append(parent_path)

from pmg_scrapers import logger

import bills
import hansards
import committees
import committee_reports


class PMGScraper(object):

    def __init__(self):
        self.stats = {}

    def scrape_bills(self):

        logger.info("\n ----------- SCRAPING BILLS ---------------")

        bill_scraper = bills.BillScraper()
        bill_scraper.run_scraper()
        logger.info(json.dumps(bill_scraper.stats, indent=4))
        return

    def scrape_hansards(self):

        logger.info("\n ----------- SCRAPING HANSARDS ---------------")

        hansard_scraper = hansards.HansardScraper()
        hansard_scraper.run_scraper()
        logger.info(json.dumps(hansard_scraper.stats, indent=4))
        return


    def scrape_committees(self):

        logger.info("\n ----------- SCRAPING COMMITTEES ---------------")

        committee_scraper = committees.CommitteeScraper()
        committee_scraper.run_scraper()
        logger.info(json.dumps(committee_scraper.stats, indent=4))
        return


    def scrape_committee_reports(self):

        logger.info("\n ----------- SCRAPING COMMITTEE REPORTS ---------------")

        report_scraper = committee_reports.ReportScraper()
        report_scraper.run_scraper()
        logger.info(json.dumps(report_scraper.stats, indent=4))
        return


def rebuild_db():

    from pmg_backend.models import Agent
    from pmg_backend import db

    db.drop_all()
    db.create_all()

    tmp = [
        ("National Assembly", "house", 1),
        ("National Council Of Provinces", "house", 2),
        ("The President", "president", 4),
        ]
    for name, agent_type, location in tmp:
        agent = Agent()
        agent.name = name
        agent.type = agent_type
        agent.location = location
        db.session.add(agent)

    db.session.commit()
    return


if __name__ == "__main__":

    # locations = [
    #     (None, "Unknown"),
    #     (1, "National Assembly (NA)"),
    #     (2, "National Council of Provinces (NCOP)"),
    #     (3, "Under joint consideration, NA + NCOP"),
    #     (4, "President's Office"),
    #     ]

    start_time = datetime.datetime.now()
    logger.info("Started at " + str(start_time))

    rebuild_db()

    scraper = PMGScraper()
    scraper.scrape_bills()
    scraper.scrape_hansards()
    scraper.scrape_committees()
    scraper.scrape_committee_reports()

    logger.info("Finished scraping at " + str(datetime.datetime.now()))
    logger.info("Duration: " + str(datetime.datetime.now() - start_time))

    import bill_status
    bill_status.find_current_bills()
    bill_status.find_enacted_bills()
    bill_status.handle_assent()