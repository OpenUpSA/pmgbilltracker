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
    def __init__(self, start_url):
        self.current_committee = None
        self.current_report = None
        self.current_url = start_url
        self.current_page = scrapertools.URLFetcher(self.current_url).html
        self.stats = {
            "total_committee_reports": 0,
            "new_committee_reports": 0,
            "errors": []
        }

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

        while True:
            soup = BeautifulSoup(self.current_page)
            reports_tab = soup.find(id="quicktabs_tabpage_committees_tabs_1")
            if reports_tab is None:
                print("No reports tab for this committee: " + self.current_url)
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

                        self.stats["errors"].append(msg)
                        pass
            if not self.next_page:
                break

    def run_scraper(self):

        try:
            state = open('tmp_state.json', 'r')
            current_agent_id = int(json.loads(state.read())['current_agent_id'])
            state.close()
        except Exception:
            logger.info("Starting from scratch.")
            current_agent_id = 0
            pass

        committees = Agent.query.filter(Agent.type == "committee").filter(Agent.agent_id >= current_agent_id)
        shuffle(committees)  # randomize the order, just to keep things interesting
        tmp_count = len(committees)
        i = 0
        for committee in committees:
            i += 1
            self.current_committee = committee
            logger.debug("agent_id: " + str(committee.agent_id))

            # resume where we were previously
            # TODO: this should not be necessary
            state = open('tmp_state.json', 'w')
            state.write('{"current_agent_id": ' + str(committee.agent_id) + '}')
            state.close()

            self.scrape_committee()
            logger.debug(str(i) + " out of " + str(tmp_count) + " committees' reports have been scraped.")


            # commit entries to database, once per committee
            db.session.commit()


    def scrape_committee(self):

        report_pager = ReportScraper(committee_url)
        for (j, (date, title, href_report)) in enumerate(report_pager.next_report):
            logger.debug("\t\t" + str(date) + " - " + title)
            time.sleep(0.25)
            tmp_url = href_report
            html = scrapertools.URLFetcher(tmp_url).html
            soup = BeautifulSoup(html)
            content = soup.find(id="content")
            bills = scrapertools.find_bills(str(content))
            # only save report entries that can be tagged to bills
            if bills:
                self.current_report = {
                    "entry_type": "committee_meeting",
                    "bills": bills,
                    "url": tmp_url,
                    "date": date,
                    "title": title,
                }
                if self.current_committee.location:
                    self.current_report["location"] = self.current_committee.location

                # TODO: filter by date
                report = Entry.query.filter(Entry.agent_id==self.current_committee.agent_id) \
                    .filter(Entry.title==self.current_report['title']).first()
                if report is None:
                    report = Entry()
                    report.agent = self.current_committee
                    self.stats["new_committee_reports"] += 1
                report = scrapertools.populate_entry(report, self.current_report, bills)
                self.current_report = {}
                db.session.add(report)
                self.stats["total_committee_reports"] += 1
        return


if __name__ == "__main__":

    tmp = [
        "http://www.pmg.org.za/committees/Ad Hoc Committee on Protection of State Information Bill (NA)",
        "http://www.pmg.org.za/committees/Reparation Committee",
        "http://www.pmg.org.za/committees/committees/Ad Hoc Committee on Protection of State Information Bill (NCOP)",
        ]
    for url in tmp:
        reports = run_scraper(url)


