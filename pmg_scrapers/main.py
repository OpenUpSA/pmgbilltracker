from __future__ import print_function
import json
import datetime
import requests

import bills
import hansards
import committees
import committee_reports
import bill_status

from pmg_scrapers import logger
from pmg_backend.models import Agent
from pmg_backend import db
from .scraper_config import config


class PMGScraper(object):

    def __init__(self):
        # login and start session with pmg website
        logger.info("LOGGING IN")
        self.session = requests.Session()
        headers = {'user-agent': 'Mozilla/4.0 (compatible: MSIE 6.0)'}
        try:
            data = {
                'name': config['name'],
                'pass': config['pass'],
                'form_id': 'user_login',
                'form_build_id': 'form-ee72095493d7ed912673b8a83219772c',
                'op': 'Log in'
            }
            r = self.session.post('http://www.pmg.org.za/user/login', headers=headers, data=data)

            if not "Welcome back." in r.content:
                logger.error("Login was not successful")
                raise Exception

        except Exception as e:
            import traceback; traceback.print_exc()
            logger.error("Configuration Error:")
            logger.error("Please ensure that a file called 'scraper_config.json' exists in the scraper directory, and that it contains" \
                  "valid 'username' and 'password' parameters for logging in to the PMG website. This is needed for accessing " \
                  "much of the content.")
            raise e
        self.stats = {}

    def scrape_bills(self):

        logger.info("\n ----------- SCRAPING BILLS ---------------")

        bill_scraper = bills.BillScraper(self.session)
        bill_scraper.run_scraper()
        logger.info(json.dumps(bill_scraper.stats, indent=4))
        return

    def scrape_hansards(self):

        logger.info("\n ----------- SCRAPING HANSARDS ---------------")

        hansard_scraper = hansards.HansardScraper(self.session)
        hansard_scraper.run_scraper()
        logger.info(json.dumps(hansard_scraper.stats, indent=4))
        return

    def scrape_committees(self):

        logger.info("\n ----------- SCRAPING COMMITTEES ---------------")

        committee_scraper = committees.CommitteeScraper(self.session)
        committee_scraper.run_scraper()
        logger.info(json.dumps(committee_scraper.stats, indent=4))
        return

    def scrape_committee_reports(self):

        logger.info("\n ----------- SCRAPING COMMITTEE REPORTS ---------------")

        report_scraper = committee_reports.ReportScraper(self.session)
        report_scraper.run_scraper()
        logger.info(json.dumps(report_scraper.stats, indent=4))
        return

    def rebuild_db(self):

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

    def run(self, rebuild_db=False, set_status=False):

        start_time = datetime.datetime.now()
        logger.info("Started at " + str(start_time))

        # start with a clean db if needed
        if rebuild_db:
            self.rebuild_db()

        # scrape content, and add to db
        self.scrape_bills()
        self.scrape_hansards()
        self.scrape_committees()
        self.scrape_committee_reports()

        # update historic bill status data
        if set_status:
            bill_status.find_current_bills()
            bill_status.find_enacted_bills()
            bill_status.handle_assent()

        logger.info("Finished scraping at " + str(datetime.datetime.now()))
        logger.info("Duration: " + str(datetime.datetime.now() - start_time))
        return
