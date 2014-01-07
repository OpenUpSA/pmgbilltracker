import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson
from random import shuffle


def populate_entry(entry, data, bill_codes=None):
    # populate bill relations
    if bill_codes:
        for code in bill_codes:
            tmp_bill = Bill.query.filter(Bill.code==code).first()
            if tmp_bill:
                entry.bills.append(tmp_bill)
            else:
                print("Could not find related bill: " + code)
                pass
    # populate required fields
    entry.type = data['entry_type']
    entry.date = data['date']
    entry.title = data['title']
    # populate optional fields
    if data.get("description"):
        entry.description = data['description']
    if data.get("location"):
        entry.location = data['location']
    if data.get("stage"):
        entry.stage = data['stage']
    if data.get("url"):
        entry.url = data['url']
    return entry


def scrape_bills(DEBUG=True):
    import bills

    print "\n ----------- SCRAPING BILLS ---------------"
    bill_dict, draft_list = bills.run_scraper(DEBUG)
    print str(len(bill_dict)) + " Bills scraped"
    print str(len(draft_list)) + " Draft bills scraped"

    # save scraped bills to database
    for bill_code, bill_data in bill_dict.iteritems():
        bill = Bill.query.filter(Bill.code==bill_code).first()
        if bill is None:
            bill = Bill()
            bill.code = bill_code
        bill.name = bill_data['bill_name']
        if bill_data.get('introduced_by'):
            bill.introduced_by = bill_data['introduced_by']
        bill.year = bill_data['year']
        bill.bill_type = bill_data['type']
        bill.number = bill_data['number']
        db.session.add(bill)
        # save related bill versions
        for entry_data in bill_data['versions']:
            entry = Entry.query.filter(Entry.url==entry_data['url']).first()  # Look for pre-existing entry.
            if entry is None:
                entry = Entry()  # Create new entry.
            entry_data["entry_type"] = "version"
            entry = populate_entry(entry, entry_data)
            entry.bills.append(bill)
            db.session.add(entry)
    db.session.commit()

    # save scraped draft bills to database
    for draft in draft_list:
        bill = Bill.query.filter(Bill.name==draft['bill_name']).filter(Bill.year==draft['year']).first()
        if bill is None:
            bill = Bill()
            bill.name = draft['bill_name']
            bill.year = draft['year']
        bill.bill_type = draft['type']
        if draft.get('introduced_by'):
            bill.introduced_by = draft['introduced_by']
        db.session.add(bill)
        # save related bill versions
        for entry_data in draft['versions']:
            entry = Entry.query.filter(Entry.url==entry_data['url']).first()  # Look for pre-existing entry.
            if entry is None:
                entry = Entry()  # Create new entry.
            entry_data["entry_type"] = "version"
            entry = populate_entry(entry, entry_data)
            entry.bills.append(bill)
            db.session.add(entry)
    db.session.commit()
    return


def scrape_hansards(DEBUG=True):

    import hansards
    print "\n ----------- SCRAPING HANSARDS ---------------"

    count_tags = 0

    hansard_list = hansards.run_scraper(DEBUG)

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
    print str(len(hansard_list)) + " Hansards scraped"
    print str(count_tags) + " Hansards tagged to bills"
    return


def scrape_committees(DEBUG=True):
    """
    Scrape list of committees from PMG.
    """

    import committees
    print "\n ----------- SCRAPING COMMITTEES ---------------"
    committee_list = committees.run_scraper(DEBUG)
    print str(len(committee_list)) + " Committees scraped"

    # save committees to database
    for committee in committee_list:
        agent = Agent.query.filter(Agent.name==committee['name']).filter(Agent.type==committee['type']).first()
        if agent is None:
            agent = Agent()
            agent.name = committee['name']
            agent.type = committee['type']
        agent.url = committee['url']
        db.session.add(agent)
    db.session.commit()
    return


def scrape_committee_reports(DEBUG=True):
    """
    Scrape meeting reports from each committee's page.
    """

    import committee_reports
    print "\n ----------- SCRAPING COMMITTEE REPORTS ---------------"
    count_reports = 0
    count_tags = 0
    committees = Agent.query.all()  # TODO: narrow this down to committees only
    shuffle(committees)
    for committee in committees:
        reports = committee_reports.run_scraper(DEBUG, committee.url, committee.location)
        if DEBUG:
            print committee.name
            print str(len(reports)) + " reports"
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
        print str(count_reports) + " Committee meeting reports scraped"
        print str(count_tags) + " Committee meeting reports tagged to bills"
    return


if __name__ == "__main__":

    DEBUG = False

    # db.drop_all()
    # db.create_all()

    # locations = [
    #     (None, "Unknown"),
    #     (1, "National Assembly (NA)"),
    #     (2, "National Council of Provinces (NCOP)"),
    #     (3, "Under joint consideration, NA + NCOP"),
    #     (4, "President's Office"),
    #     ]
    #
    # stages = [
    #     (None, "Unknown"),
    #     (1, "Introduced"),
    #     (2, "Before committee"),
    #     (3, "Awaiting approval"),
    #     (4, "Mediation"),
    #     ]

    # scrape_bills(DEBUG)
    # scrape_hansards(DEBUG)
    # scrape_committees(DEBUG)
    scrape_committee_reports(DEBUG)
