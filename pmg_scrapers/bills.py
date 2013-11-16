"""
Scrapes all bills introduced from 2006 until now from PMG e.g.
www.pmg.org.za/bill?year=2013

Also includes links to bill versions as well as introduction date
"""
from __future__ import print_function
import sys
import requests
import json
from BeautifulSoup import BeautifulSoup
from dateutil import parser as dateparser
from datetime import datetime

def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

class URLFetcher(object):
    def __init__(self, url):
        self.url = url

    @property
    def html(self):
        r = requests.get(self.url)
        return r.content

class FileFetcher(object):
    filename = "bill"

    @property
    def html(self):
        return open(FileFetcher.filename).read()

class BillParser(object):
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

pager = Pager()

bills = []
for url in pager.next_page:
    print(url, file=sys.stderr)
    parser = BillParser()
    html = URLFetcher(url).html
    soup = BeautifulSoup(html)
    rows = soup.findAll("tr")

    for row in rows:
        while not parser.state_fn(row):
            pass
    bills.extend(parser.bills)
print(json.dumps(bills, indent=4, default=handler))
