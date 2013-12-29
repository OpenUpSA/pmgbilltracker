import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson


def scrape_bills():
    from pmg import bills
    bill_dict, draft_list = bills.run_scraper()

    print str(len(bill_dict)) + " bills scraped"
    print str(len(draft_list)) + " draft bills scraped"

    # save scraped bills to database
    for bill_id, bill in bill_dict.iteritems():
        tmp = Bill()
        tmp.name = bill['bill_name']
        tmp.code = bill_id
        if bill.get('introduced_by'):
            tmp.introduced_by = bill['introduced_by']
        tmp.year = bill['year']
        db.session.add(tmp)

    # TODO: save scraped draft bills to database
    
    return


def scrape_hansards():

    return


def scrape_committees():

    return


if __name__ == "__main__":

    db.drop_all()
    db.create_all()

    scrape_bills()

    db.session.commit()