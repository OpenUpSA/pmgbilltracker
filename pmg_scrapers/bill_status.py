import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson
from random import shuffle
from scrapertools import analyze_bill_code
from dateutil import parser as date_parser
import csv
from pmg_scrapers import logger


def find_current_bills():
    """
    Update status of most recent set of bills from http://pmg.org.za/billsstatus/proceedings, via
    the csv at /data/current_status.csv
    """

    with open("../data/current_status.csv", 'Ur') as f:
        data = list(list(rec) for rec in csv.reader(f, delimiter=','))

    for i in range(len(data)):

        # ignore column title row
        if i==0:
            continue

        entry = data[i]

        # fix bill types
        if entry[0].startswith("PM"):
            entry[0] = "PMB" + entry[0][2::]
        elif not entry[0].startswith("B"):
            entry[0] = "B" + entry[0]
        tmp_code = entry[0]
        tmp_status = entry[1].lower()

        # clean bill code
        tmp = analyze_bill_code(tmp_code)
        code = tmp["code"]

        print code + " " + str(entry)

        bill = Bill.query.filter(Bill.code==code).first()
        available_status = {
            "act": "enacted",
            "unknown": None,
            "pc": "na",
            "sc": "ncop",
            "intro": "na",
        }

        if available_status.get(tmp_status):
            tmp_status = available_status[tmp_status]
        bill.status = tmp_status
        db.session.add(bill)
    db.session.commit()
    return


def find_enacted_bills():
    """
    Set status of bills that have already been enacted.
    """

    for bill in Bill.query.all():
        for entry in bill.entries:
            if entry.type == "act":
                bill.status = "enacted"
                db.session.add(bill)
                print "enacted: " + bill.name
                break
    db.session.commit()
    return


def handle_assent():
    """
    Add entries relating to a bill's assent from http://pmg.org.za/billsstatus/proceedings, via
    the csv at /data/bill_assent_dates.csv
    """

    with open("../data/bill_assent_dates.csv", 'Ur') as f:
        data = list(list(rec) for rec in csv.reader(f, delimiter=','))

    for i in range(len(data)):

        # ignore column title row
        if i==0:
            continue

        entry = data[i]

        # fix bill types
        if entry[0].startswith("PM"):
            entry[0] = "PMB" + entry[0][2::]
        elif not entry[0].startswith("B"):
            entry[0] = "B" + entry[0]
        tmp_code = entry[0]
        tmp_status = entry[1].lower()

        # clean bill code
        tmp = analyze_bill_code(tmp_code)
        if tmp:
            code = tmp["code"]
        else:
            print "Error analyzing bill code " + tmp_code
            continue

        print code + " " + str(entry)

        bill = Bill.query.filter(Bill.code==code).first()
        if bill is None:
            print "Error finding bill " + code
            continue

        try:
            act_no = unicode(entry[1])
            assent_date = unicode(entry[2])
            # convert date to python date object
            try:
                assent_date = date_parser.parse(assent_date).date()
            except Exception:
                print "Error parsing date " + entry[2]
                continue
            if entry[3] and len(entry[3]) > 2:
                gazette = unicode(entry[3])
        except UnicodeDecodeError:
            print "Unicode error: " + str(entry)
            continue

        # update bill record
        bill.status = "enacted"
        if gazette:
            bill.gazette = gazette
        db.session.add(bill)

        # add relevant entry in bill history
        tmp_entry = Entry.query.join(Entry.bills).filter(Bill.code==code).filter(Entry.type=="assent").first()
        if not tmp_entry:
            tmp_entry = Entry()
            tmp_entry.bills.append(bill)
        tmp_entry.date = assent_date
        tmp_entry.type = "assent"
        tmp_entry.location = 4
        tmp_entry.title = "Signed into law by the President."
        if act_no and gazette:
            tmp_entry.description = "Enacted as Act " + act_no + ". Refer to Government Gazette " + gazette + "."
        db.session.add(tmp_entry)
    db.session.commit()
    return

if __name__ == "__main__":

    find_current_bills()
    find_enacted_bills()
    handle_assent()

    # tmp_entries = Entry.query.filter(Entry.type=="assent").all()
    # for entry in tmp_entries:
    #     db.session.delete(entry)
    # db.session.commit()
