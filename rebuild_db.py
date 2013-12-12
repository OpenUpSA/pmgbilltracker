import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson

tmp = open('db_sources/na_reports.json', 'r')
na_reports = simplejson.load(tmp)
tmp.close()

tmp = open('db_sources/na_hearings.json', 'r')
na_hearings = simplejson.load(tmp)
tmp.close()

tmp = open('db_sources/ncop_reports.json', 'r')
ncop_reports = simplejson.load(tmp)
tmp.close()

tmp = open('db_sources/ncop_hearings.json', 'r')
ncop_hearings = simplejson.load(tmp)
tmp.close()

tmp = open('db_sources/all_bills.json', 'r')
# TODO: clean input file to avoid duplicate entries
all_bills = simplejson.load(tmp)
tmp.close()


def new_report(report_dict, tmp_bill, tmp_location, tmp_stage, tmp_agent, entry_type):

    tmp_date = report_dict['date'][0]
    # convert date string to datetime object
    if len(tmp_date) == 10:
        tmp_date = "0" + tmp_date
    tmp_date = datetime.datetime.strptime(tmp_date, "%d %b %Y")

    tmp_link = report_dict['link'][0]
    tmp_title = report_dict['title'][0]

    entry = Entry()
    entry.bills = [tmp_bill,]
    entry.date = tmp_date
    entry.location = tmp_location
    entry.stage = tmp_stage
    entry.agent = tmp_agent
    entry.type = entry_type
    entry.title = tmp_title
    entry.url = "http://www.pmg.org.za" + tmp_link
    return entry


def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    db.drop_all()
    db.create_all()

    locations = [
        (None, "Unknown"),
        (1, "National Assembly (NA)"),
        (2, "National Council of Provinces (NCOP)"),
        (3, "President's Office"),
        ]

    stages = [
        (None, "Unknown"),
        (1, "Introduced"),
        (2, "Before committee"),
        (3, "Awaiting approval"),
        (4, "Mediation"),
        ]

    b1 = Bill()
    b1.name = 'Protection of State Information Bill'
    b1.code = "B6"
    b1.year = 2010
    b1.status = "110"
    b1.introduced_by = "Minister of State Security"
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    b1.draft = 'uploads/example.pdf'
    b1.white_paper = 'uploads/example.pdf'
    b1.green_paper = 'uploads/example.pdf'
    b1.gazette = 'uploads/Gazette-32999_2010-03-05.pdf'
    db.session.add(b1)

    log = []
    for bill in all_bills:
        # test for draft bills
        code = bill['bill_number'].lower().replace("x", "")
        if (not "draft" in bill['bill_name'].lower()) and len(code) > 1:
            if not bill['bill_name'] == "Protection Of Information Bill":
                tmp = Bill()
                tmp.name = bill["bill_name"]
                tmp.code = bill["bill_number"].replace("Bill ", "B")
                if bill.get("introduced_by"):
                    tmp.introduced_by = bill["introduced_by"]
                if bill.get("versions"):
                    tmp.year = int(bill["versions"][-1]["date"][0:4])
                unique = str(tmp.year) + " " + tmp.code
                while unique in log:
                    tmp.code += " II"
                    unique += " II"

                db.session.add(tmp)
                log.append(unique)

    agent_details = [
        ("house", "National Assembly", "NA"),
        ("house", "National Council of Provinces", "NA"),
        ("na-committee", "Ad-Hoc Committee on Protection of State Information Bill", "Ad-Hoc Committee"),
        ("ncop-committee", "Ad-Hoc Committee on Protection of State Information Bill", "Ad-Hoc Committee"),
        ("joint-committee", None, None),
        ("minister", "Minister of State Security", None),
        ("president", "The President of the Republic of South Africa", "President"),
        ("mp", None, None),
        ]

    agents = []
    for tmp in agent_details:
        agent = Agent()
        agent.type = tmp[0]
        agent.name = tmp[1]
        agent.short_name = tmp[2]
        db.session.add(agent)
        agents.append(agent)

    bill_entries = [
        (datetime.date(2010, 3, 4), "bill", 1, 1, agents[5], "uploads/B6-2010.pdf", "Protection of State Information Bill [B6 2010]"),
        (datetime.date(2011, 9, 4), "bill", 1, 2, agents[2], "uploads/B6B-2010.pdf", "Protection of State Information Bill [B6B 2010]"),
        (datetime.date(2013, 4, 24), "bill", 1, 2, agents[2], "uploads/B6C-2010.pdf", "Protection of State Information Bill [B6C 2010]"),
        (datetime.date(2013, 4, 24), "bill", 1, 2, agents[2], "uploads/B6D-2010.pdf", "Protection of State Information Bill [B6D 2010]"),
        (datetime.date(2013, 10, 15), "bill", 1, 2, agents[2], "uploads/B6E-2010.pdf", "Protection of State Information Bill [B6E 2010]"),
        (datetime.date(2013, 10, 15), "bill", 1, 2, agents[2], "uploads/B6F-2010.pdf", "Protection of State Information Bill [B6F 2010]"),
        ]

    for tmp in bill_entries:
        entry = Entry()
        entry.bills = [b1,]
        entry.date = tmp[0]
        entry.type = tmp[1]
        entry.location = tmp[2]
        entry.stage = tmp[3]
        entry.agent = tmp[4]
        entry.url = tmp[5]
        entry.title = tmp[6]
        db.session.add(entry)

    for na_report in na_reports:
        tmp_entry = new_report(na_report, b1, 1, 2, agents[2], "pmg-meeting-report")
        db.session.add(tmp_entry)

    for na_report in na_hearings:
        tmp_entry = new_report(na_report, b1, 1, 2, agents[2], "public-hearing-report")
        db.session.add(tmp_entry)

    for ncop_report in ncop_reports:
        tmp_entry = new_report(ncop_report, b1, 2, 2, agents[3], "pmg-meeting-report")
        db.session.add(tmp_entry)

    for ncop_report in ncop_hearings:
        tmp_entry = new_report(ncop_report, b1, 2, 2, agents[3], "public-hearing-report")
        db.session.add(tmp_entry)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()