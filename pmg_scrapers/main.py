from __future__ import print_function
import datetime
import simplejson
from random import shuffle
import os
import sys

# Add the parent folder path to the sys.path list
path = os.getcwd()
tmp = path.split("/")[0:-1]
parent_path = "/".join(tmp)
sys.path.append(parent_path)

from pmg_backend.models import *
from pmg_backend import db
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

        bill_parser = bills.BillScraper()
        bill_parser.run_scraper()
        # draft_list = bill_parser.drafts
        # bill_dict = bill_parser.bills
        #
        # logger.info(str(len(bill_dict)) + " Bills scraped")
        # logger.info(str(len(draft_list)) + " Draft bills scraped")


        return


    def scrape_hansards(self):

        logger.info("\n ----------- SCRAPING HANSARDS ---------------")

        count_tags = 0

        hansard_list = hansards.run_scraper()

        for data in hansard_list:
            data['entry_type'] = "hansard"
            bills = []
            if data.get('bills'):
                bills = data["bills"]
                count_tags += len(bills)
            # TODO: improve filtering
            hansard = Entry.query.filter(Entry.type=="hansard").filter(Entry.title==data['title']).first()
            if hansard is None:
                hansard = Entry()
            hansard = populate_entry(hansard, data, bills)
            db.session.add(hansard)
        db.session.commit()
        logger.info(str(len(hansard_list)) + " Hansards scraped")
        logger.info(str(count_tags) + " Hansards tagged to bills")
        return


    def scrape_committees(self):
        """
        Scrape list of committees from PMG.
        """

        logger.info("\n ----------- SCRAPING COMMITTEES ---------------")
        committee_list = committees.run_scraper()
        logger.info(str(len(committee_list)) + " Committees scraped")

        # save committees to database
        for committee in committee_list:
            agent = Agent.query.filter(Agent.name==committee['name']).filter(Agent.type==committee['type']).first()
            if agent is None:
                agent = Agent()
                agent.name = committee['name']
                agent.type = committee['type']
                agent.location = committee['location']
            agent.url = committee['url']
            db.session.add(agent)
        db.session.commit()
        return


    def scrape_committee_reports(self):
        """
        Scrape meeting reports from each committee's page.
        """

        logger.info("\n ----------- SCRAPING COMMITTEE REPORTS ---------------")
        count_reports = 0
        count_tags = 0

        try:
            state = open('tmp_state.json', 'r')
            current_agent_id = int(simplejson.loads(state.read())['current_agent_id'])
            state.close()
        except Exception:
            logger.info("Starting from scratch.")
            current_agent_id = 0
            pass

        committees = Agent.query.filter(Agent.agent_id >= current_agent_id).order_by(Agent.agent_id)  # TODO: narrow this down to committees only
        # shuffle(committees)
        for committee in committees:
            logger.debug("agent_id: " + str(committee.agent_id))
            state = open('tmp_state.json', 'w')
            state.write('{"current_agent_id": ' + str(committee.agent_id) + '}')
            state.close()
            reports = committee_reports.run_scraper(DEBUG, committee.url, committee.location)
            logger.debug(committee.name)
            logger.debug(str(len(reports)) + " reports")
            for data in reports:
                count_reports += 1
                data['entry_type'] = "committee_meeting"
                bills = []
                if data.get('bills'):
                    bills = data["bills"]
                    count_tags += len(bills)
                # TODO: filter by date
                report = Entry.query.filter(Entry.agent_id==committee.agent_id).filter(Entry.title==data['title']).first()
                if report is None:
                    report = Entry()
                    report.agent = committee
                report = populate_entry(report, data, bills)
                db.session.add(report)
            db.session.commit()
            logger.info(str(count_reports) + " Committee meeting reports scraped")
            logger.info(str(count_tags) + " Committee meeting reports tagged to bills")
        return


if __name__ == "__main__":

    # locations = [
    #     (None, "Unknown"),
    #     (1, "National Assembly (NA)"),
    #     (2, "National Council of Provinces (NCOP)"),
    #     (3, "Under joint consideration, NA + NCOP"),
    #     (4, "President's Office"),
    #     ]

    # db.drop_all()
    # db.create_all()

    scraper = PMGScraper()
    scraper.scrape_bills()
    scraper.scrape_hansards()
    scraper.scrape_committees()
    scraper.scrape_committee_reports()

    import bill_status
    bill_status.find_current_bills()
    bill_status.find_enacted_bills()
    bill_status.handle_assent()