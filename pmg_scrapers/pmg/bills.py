"""
Scrapes all bills introduced from 2006 until now from PMG e.g.
www.pmg.org.za/bill?year=2013, while including links to bill versions and the introduction date
"""
from __future__ import print_function
import sys
import json
from BeautifulSoup import BeautifulSoup
from dateutil import parser as date_parser
from datetime import datetime
import pmg_scrapers.scrapertools
import string

DEBUG = False

class BillParser(object):
    """
    State machine for extracting a list of bills from an html table. It operates on a list of table rows, extracting
    one bill at a time.

    The calling function should keep calling the method stored in 'state_fn', which will return True once it is
    finished parsing a particular row.

    Bills look like:
    <tr class="odd"><td colspan="2"><strong>Bill 30 - Marine Living Resources Amendment Bill</strong></td> </tr>
    <tr class="even"><td>&nbsp;&nbsp;&nbsp;&nbsp;<a href="/bill/20131029-marine-living-resources-amendment-bill-b30b-2013">B30B-2013</a></td><td>29 Oct, 2013</td> </tr>
    """
    def __init__(self):
        self.state_fn = self.start_state
        self.bills = {}
        self.drafts = []
        self.current_bill = {}

    def start_state(self, fragment):
        """
        Inititialize State Machine
        """
        if not fragment.find("strong"):
            return True

        self.state_fn = self.header_state
        return False

    def header_state(self, fragment):
        """
        Extract info from header row.
        """
        if not fragment.find("strong"):
            raise Exception("Unknown state")

        if self.current_bill:
            try:
                self.bills[self.current_bill["bill_id"]] = self.current_bill
            except KeyError:
                if self.current_bill['bill_type'] == "Draft":
                    self.drafts.append(self.current_bill)
                else:
                    print("Bill cannot be identified")
                    print(json.dumps(self.current_bill, indent=4, default=pmg_scrapers.scrapertools.handler))
                    raise
            if DEBUG:
                print(json.dumps(self.current_bill, indent=4, default=pmg_scrapers.scrapertools.handler))
            self.current_bill = {}

        text = fragment.text
        parts = text.split("-")
        self.current_bill["bill_name"] = parts[1].strip()
        if len(parts) == 3:
            self.current_bill["introduced_by"] = parts[2].strip()

        self.state_fn = self.version_state
        return True

    def version_state(self, fragment):
        """
        Extract available versions from second row.
        """
        link = fragment.find("a")
        if link: 
            versions = self.current_bill.setdefault("versions", [])
            url = link["href"]
            if not self.current_bill.get("bill_type"):
                tmp = link.text
                info = parse_bill_code(tmp)
                self.current_bill = dict(self.current_bill.items() + info.items())
            version = {
                "url" : link["href"],
                "name" : link.text,
                "date" : date_parser.parse(fragment.findAll("td")[1].text).date(),
            }
            versions.append(version)
            self.state_fn = self.version_state
            return True
        else:
            self.state_fn = self.header_state
            return False


def parse_bill_code(code):
    """
    Extract information about a bill, from codes such as:
        B6-2010
        B6F-2010
        B4-2010 - as enacted
        B - 2010
        PMB5-2013
    """

    code = code.strip()
    out = {}

    if not "-" in code:
        if code[-4::].isdigit():
            code = code[0:-4] + "-" + code[-4::]
        else:
            print("Error parsing code: " + code)
            raise ValueError

    components = code.split("-")

    # extract year
    year = None
    for comp in components:
        try:
            year = int(comp)
            break
        except (IndexError, ValueError) as e:
            pass
    out["year"] = year

    # extract bill number
    bill_number = None
    tmp = ""
    tmp_str = components[0].strip()
    for i in range(len(tmp_str)):
        if tmp_str[i] in string.ascii_letters + " ":
            pass
        else:
            tmp += tmp_str[i]
    if len(tmp) > 0:
        bill_number = int(tmp)
    out["bill_number"] = bill_number

    # extract bill type
    bill_type = None
    if code.startswith("PMB"):
        bill_type = "PMB"
    elif code.startswith("B"):
        bill_type = "B"
    if "as enacted" in code:
        bill_type = "Act"
    if not bill_number:
        bill_type = "Draft"
    out['bill_type'] = bill_type

    # extract version
    version = None
    tmp = components[0]
    if bill_number and bill_number != "X":
        version = tmp.split(str(bill_number))[-1]

    # assemble id string
    if bill_type and bill_number and year:
        prefix = "B"
        if bill_type == "PMB":
            prefix = "PMB"
        bill_id = prefix + str(bill_number) + "-" + str(year)
        out["bill_id"] = bill_id
    return out


class Pager(object):
    """
    Return an iterable containing URLs to each of the available bills pages.
    """
    @property
    def next_page(self):
        if DEBUG:
            yield "http://www.pmg.org.za/print/bill?year=2013"
        else:
            current_year = datetime.today().year
            for current_year in range(current_year, 2005, -1):
                url = "http://www.pmg.org.za/print/bill?year=%d" % current_year
                yield url


if __name__ == "__main__":

    DEBUG = True

    # for code in ["B6-2010", "B6F-2010", "B4-2010 - as enacted", "B - 2010", "PMB5-2013"]:
    #     print(code)
    #     print(parse_bill_code(code))

    pager = Pager()
    bills = []

    # iterate through bill pages
    for url in pager.next_page:
        print(url, file=sys.stderr)

        # initiate parser for this page
        parser = BillParser()
        html = pmg_scrapers.scrapertools.URLFetcher(url).html
        soup = BeautifulSoup(html)
        rows = soup.findAll("tr")

        # feed rows into state machine
        for row in rows:
            while not parser.state_fn(row):
                pass

        # save extracted content for this page
        bills.extend(parser.bills)

    # # do something with scraped data
    # print(json.dumps(bills, indent=4, default=pmg_scrapers.scrapertools.handler))
