import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson
from random import shuffle
from scrapertools import analyze_bill_code

import csv


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


if __name__ == "__main__":

    find_current_bills()
    find_enacted_bills()
