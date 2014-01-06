import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson
from random import shuffle
from scrapertools import analyze_bill_code

import csv

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
        "pc": "na_committee",
        "sc": "ncop_committee",
        "intro": "na-introduced",
    }

    if available_status.get(tmp_status):
        tmp_status = available_status[tmp_status]
    bill.status = tmp_status
    db.session.add(bill)
db.session.commit()



