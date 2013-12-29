import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson


def populate_entry(entry, data, bill_codes):
    # populate bill relations
    for code in bill_codes:
        tmp_bill = Bill.query.filter(Bill.code==code).first()
        if tmp_bill:
            entry.bills.append(tmp_bill)
        else:
            print("Could not find related bill.")
            raise Exception
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


def scrape_bills(DEBUG):
    from pmg import bills
    bill_dict, draft_list = bills.run_scraper(DEBUG)

    print str(len(bill_dict)) + " bills scraped"
    print str(len(draft_list)) + " draft bills scraped"

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
        bill.bill_type = bill_data['bill_type']
        db.session.add(bill)
        db.session.commit()
        # save related bill versions
        for entry_data in bill_data['versions']:
            entry = Entry.query.filter(Entry.url==entry_data['url']).first()  # Look for pre-existing entry.
            if entry is None:
                entry = Entry()  # Create new entry.
            entry_data["entry_type"] = "bill_version"
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
        bill.bill_type = draft['bill_type']
        if draft.get('introduced_by'):
            bill.introduced_by = draft['introduced_by']
        db.session.add(bill)
        db.session.commit()

    return


def scrape_hansards():

    return


def scrape_committees():

    return


if __name__ == "__main__":

    DEBUG = True

    # db.drop_all()
    # db.create_all()

    scrape_bills(DEBUG)

    db.session.commit()