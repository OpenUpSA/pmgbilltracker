from pmg_backend import db
from pmg_backend.models import *
import json
import os

bills = Bill.query.filter_by(is_deleted=False).all()

print len(bills)

out = []
for bill in bills:
    tmp_bill = {
        'name': bill.name,
        'code': bill.code,
        'bill_type': bill.bill_type,
        'year': bill.year,
        'number': bill.number,
        'status': bill.status,
        'entries': [],
    }

    for entry in bill.entries:
        if not entry.is_deleted:
            tmp_bill['entries'].append({
                'date': str(entry.date),
                'type': entry.type,
                'title': entry.title,
                'description': entry.description,
                'location': entry.location,
                'agent': {
                    'type': entry.agent.type if entry.agent else None,
                    'name': entry.agent.name.strip() if entry.agent else None,
                },
                'url': entry.url,
            })
    out.append(tmp_bill)
    #     print json.dumps(tmp_entry, indent=4)
    # print ""


with open("billtracker_dump.txt", "w") as text_file:
    text_file.write(json.dumps(out, indent=4))