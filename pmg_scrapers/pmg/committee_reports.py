"""
Scrapes committee reports from PMG e.g.
http://www.pmg.org.za/committees
"""
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
from dateutil import parser as dateparser
from datetime import datetime
from pmg_scrapers import scrapertools

class ReportParser(object):
    def __init__(self):
        self.state_fn = self.start_state
        self.bills = []

    def start_state(self, fragment):
        if not fragment.find("strong"):
            return True

        self.state_fn = self.header_state
        return False


    def header_state(self, fragment):
        if not fragment.find("strong"):
            raise Exception("Unknown state")
            
        self.current_bill = {}
        self.bills.append(self.current_bill)

        text = fragment.text
        text = text.replace(u"\u2013", "-")
        parts = text.split("-")
        self.current_bill["bill_number"] = parts[0].strip()
        self.current_bill["bill_name"] = parts[1].strip()
        if len(parts) == 3:
            self.current_bill["introduced_by"] = parts[2].strip()

        self.state_fn = self.version_state
        return True

    def version_state(self, fragment):
        link = fragment.find("a")
        if link: 
            versions = self.current_bill.setdefault("versions", [])
            url = link["href"]
            versions.append({
                "url" : link["href"],
                "name" : link.text,
                "date" : dateparser.parse(fragment.findAll("td")[1].text),
            })
            self.state_fn = self.version_state
            return True
        else:
            self.state_fn = self.header_state
            return False


class ReportPager(object):
    current_url = None
    current_page = None

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

    # committee_pager = CommitteePager()
    # for (index, (list_name, href, name)) in enumerate(committee_pager.next_committee):
    #     if index == 0:
    #         sample = list_name, href, name
    #     print("\t" + str(index+1) + ": " + name)

    list_name, href, name = (u'National Assembly Committees', u'/committees/Agriculture, Forestry and Fisheries', u'Agriculture, Forestry and Fisheries')

    report_pager = ReportPager(href)
    for report in report_pager.next_report:
        print(report)

