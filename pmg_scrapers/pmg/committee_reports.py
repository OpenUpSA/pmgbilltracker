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

re_bill = re.compile("""
        (            # Capture the following match
                     # Match a bill code that looks something like [B9B - 2004]
        \[           # Match the first bracket
        \s*          # White space after the bracket
        [PM]*B       # Bills start with a B, or a PMB.
        \s*          # More whitespace after the B
        [0-9]+[A-Z]* # Bill number e.g. 10A (the letter might be missing)
        \s*-\s*      # The hyphen might be surrounded by whitespace
        [0-9]{4}     # Search for a 4 digit year
        \s*\]        # Round off by finding a closing square bracket preceeded by optional spaces
        )            # close the capture
""", re.IGNORECASE | re.VERBOSE)


class ReportParser(object):
    def __init__(self, report_url):
        self.report_url = report_url
        self.bills = []

    def find_bills(self):
        html = scrapertools.URLFetcher("http://www.pmg.org.za" + self.report_url).html
        for res in re_bill.finditer(html):
            bill_str = res.group(1).replace(" ", "")[1:-1]
            # disregard different versions of the same bill
            code, year = bill_str.split("-")
            code = code[1::]
            try:
                tmp = int(code)
            except ValueError:
                code = code[0:-1]
                bill_str = "B" + code + "-" + year
            if not bill_str in self.bills:
                self.bills.append(bill_str)
        return self.bills


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

    f = open('committee_meetings.json', 'w')
    f.write('[\n')
    count = 0
    committee_pager = CommitteePager()
    for (i, (list_name, href_committee, name)) in enumerate(committee_pager.next_committee):
        print("\t" + str(i+1) + ": " + name)
        report_pager = ReportPager(href_committee)
        for (j, (date, title, href_report)) in enumerate(report_pager.next_report):
            print("\t\t" + date + " - " + title)
            report_parser = ReportParser(href_report)
            bills = report_parser.find_bills()
            if bills:
                if count != 0:
                    f.write(",\n")
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
                f.write(simplejson.dumps(entry, indent=4))
    f.writeln(']')
    f.close()