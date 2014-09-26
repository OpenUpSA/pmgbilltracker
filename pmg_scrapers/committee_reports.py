"""
Scrapes committee reports from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
from dateutil import parser as date_parser
import scrapertools
import time
from pmg_scrapers import logger
from pmg_backend.models import *
from pmg_backend import db
import json
from random import shuffle


class ReportScraper(object):

    def __init__(self, session):
        self.session = session
        self.current_committee = None
        self.current_report = None
        self.current_url = None
        self.current_page = None
        self.stats = {
            "total_committee_reports": 0,
            "new_committee_reports": 0,
            "errors": []
        }

    @property
    def next_page(self):
        """
        Extract the 'next' link, if there is one.
        """
        soup = BeautifulSoup(self.current_page)
        reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
        next_link = reports_tab.find("li", {"class": "pager-next"})
        if next_link:
            href = "http://www.pmg.org.za" + next_link.find('a').attrs[0][1]
            self.current_url = href
            self.current_page = scrapertools.URLFetcher(self.current_url, self.session).html
            return True
        return False

    @property
    def next_report(self):
        """
        Iterate over the reports listed on a particular page.
        """
        while True:
            soup = BeautifulSoup(self.current_page, convertEntities=BeautifulSoup.HTML_ENTITIES)
            reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
            if reports_tab is None:
                logger.error("No reports tab for this committee: " + self.current_url)
                break
            table_body = reports_tab.find("tbody")

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
                        msg = "Error reading committee report details from table row: "
                        msg += self.current_url
                        self.stats["errors"].append(msg)
                        pass
            else:
                logger.error("No table body")
            if not self.next_page:
                break
        return

    def scrape_committee(self):
        """
        Scrape all meeting reports for a particular committee.
        """

        for (j, (date, title, href_report)) in enumerate(self.next_report):
            logger.debug("\t\t" + str(date) + " - " + (title[0:45]) if len(title) > 45 else title)
            tmp_url = href_report
            html = scrapertools.URLFetcher(tmp_url, self.session).html
            soup = BeautifulSoup(html)
            content = soup.find(id="content")
            bills = scrapertools.find_bills(str(content))
            # only save report entries that can be tagged to bills
            if bills:
                self.current_report = {
                    "entry_type": "committee-meeting",
                    "bills": bills,
                    "url": tmp_url,
                    "date": date,
                    "title": title,
                    "agent": self.current_committee,
                    }

                # report URL may have changed after editing on pmg.org.za, check for this
                possible_duplicates = Entry.query.filter_by(Entry.agent == self.current_committee)\
                    .filter(Entry.url != None)\
                    .filter(Entry.url != tmp_url)\
                    .filter(Entry.type == "committee-meeting")\
                    .filter(Entry.is_deleted == False)\
                    .filter(Entry.date == date)\
                    .order_by(Entry.entry_id).all()
                deletion_flag = False
                if possible_duplicates:
                    logger.debug(str(len(possible_duplicates)) + " possible duplicates found")
                    for possible_duplicate in possible_duplicates:
                        redirect_url = scrapertools.URLFetcher(possible_duplicate.url, self.session).follow_redirect()
                        if possible_duplicate.url != redirect_url:
                            logger.debug('redirect encountered')
                            if redirect_url == tmp_url:
                                logger.info("Updating entry URL")
                                # update the existing record's URL
                                possible_duplicate.url = tmp_url
                                # # delete all but one entry, if there are multiple duplicates
                                # if deletion_flag:
                                #     logger.info('duplicate entry deleted')
                                #     possible_duplicate.is_deleted = True
                                db.session.add(possible_duplicate)
                                deletion_flag = True

                if self.current_committee.location:
                    self.current_report["location"] = self.current_committee.location
                try:
                    self.add_or_update()
                except Exception, e:
                    msg = "Could not add committee report to database: "
                    if self.current_report.get("title"):
                        msg += self.current_report["title"]
                    self.stats["errors"].append(msg)
                    logger.error(msg)
                    logger.exception(str(e))
                self.current_report = {}
            else:
                logger.debug('no bills found in committee meeting report')
        return

    def run_scraper(self):

        committees = Agent.query.filter(Agent.type == "committee").filter(Agent.url != None).all()
        shuffle(committees)  # randomize the order, just to keep things interesting
        for i, committee in enumerate(committees):
            self.current_committee = committee
            self.current_url = committee.url
            try:
                self.current_page = scrapertools.URLFetcher(self.current_url, self.session).html
                logger.debug("Committee: " + str(committee.name))

                self.scrape_committee()
                # give some progress feedback
                logger.info(str(i + 1) + " out of " + str(len(committees)) + " committees' reports have been scraped.")
                logger.info(json.dumps(self.stats, indent=4))

                # commit entries to database, once per committee
                logger.debug("SAVING TO DATABASE")
                db.session.commit()
            except Exception as e:
                msg = "Error scraping committee's reports."
                self.stats["errors"].append(msg)
                logger.error(msg)
                logger.exception(str(e))
        return

    def add_or_update(self):
        """
        Add current_report to database, or update the record if it already exists.
        """

        report = Entry.query.filter_by(agent_id=self.current_committee.agent_id) \
            .filter_by(url=self.current_report['url'])\
            .filter_by(is_deleted=False).first()
        if report is None:
            report = Entry()
            self.stats["new_committee_reports"] += 1

        tmp_bills = None
        if self.current_report.get('bills'):
            tmp_bills = self.current_report['bills']
            logger.info(str(tmp_bills))
        report = scrapertools.populate_entry(report, self.current_report, tmp_bills)
        db.session.add(report)
        self.stats["total_committee_reports"] += 1
        self.current_report = {}
        return


if __name__ == "__main__":

    report_scraper = ReportScraper()
    report_scraper.run_scraper()
    logger.info(json.dumps(report_scraper.stats, indent=4))
