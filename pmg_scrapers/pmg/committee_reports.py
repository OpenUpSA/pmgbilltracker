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

class Pager(object):
    @property
    def next_page(self):
        current_year = datetime.now().year
        for current_year in range(current_year, 2005, -1):
            url = "http://www.pmg.org.za/print/bill?year=%d" % current_year
            yield url

class CommitteePager(object):
    @property
    def next_page(self):
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
    committee_pager = CommitteePager()
    for (index, (list_name, href, name)) in enumerate(committee_pager.next_page):
        print("\t" + str(index+1) + ": " + name)

#
# pager = Pager()
#
# bills = []
# for url in pager.next_page:
#     print(url, file=sys.stderr)
#     parser = BillParser()
#     html = scrapertools.URLFetcher(url).html
#     soup = BeautifulSoup(html)
#     rows = soup.findAll("tr")
#
#     for row in rows:
#         while not parser.state_fn(row):
#             pass
#     bills.extend(parser.bills)
# print(json.dumps(bills, indent=4, default=scrapertools.handler))
