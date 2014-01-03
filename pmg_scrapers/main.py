import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson
from random import shuffle


def populate_entry(entry, data, bill_codes):
    # populate bill relations
    for code in bill_codes:
        tmp_bill = Bill.query.filter(Bill.code==code).first()
        if tmp_bill:
            entry.bills.append(tmp_bill)
        else:
            print("Could not find related bill: " + code)
            print("Entry: " + data['title'])
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
    from pmg import bills
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
        db.session.add(bill)
        db.session.commit()
        # save related bill versions
        for entry_data in bill_data['versions']:
            entry = Entry.query.filter(Entry.url==entry_data['url']).first()  # Look for pre-existing entry.
            if entry is None:
                entry = Entry()  # Create new entry.
            entry_data["entry_type"] = "version"
            entry = populate_entry(entry, entry_data, [bill_code, ])
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
        db.session.commit()

    return


def scrape_hansards(DEBUG=True):

    return


def scrape_committees(DEBUG=True):
    """
    Scrape list of committees from PMG.
    """
    from pmg import committees
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
    from pmg import committee_reports

    count_reports = 0
    count_tags = 0
    committees = Agent.query.all()  # TODO: narrow this down to committees only
    shuffle(committees)
    for committee in committees:
        reports = committee_reports.run_scraper(DEBUG, committee.url)
        count_reports += 1
        if DEBUG:
            print committee.name
            print str(len(reports)) + " reports"
        for data in reports:
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
        print str(count_reports) + " Committee meeting reports scraped"
        print str(count_tags) + " Committee meeting reports tagged to bills"
    return


def scrape_pmg_meeting_reports(DEBUG=True):

    return


if __name__ == "__main__":

    DEBUG = False

    # db.drop_all()
    # db.create_all()
    #
    # scrape_bills(DEBUG)
    # scrape_committees(DEBUG)
    scrape_committee_reports(DEBUG)