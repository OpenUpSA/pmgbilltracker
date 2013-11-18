import datetime
from pmg_backend.models import Bill, Agent, Location, Stage, Event, Version, Content, ContentType
from pmg_backend import db
import simplejson

tmp = open('db_sources/na_reports.json', 'r')
na_reports = simplejson.load(tmp)
tmp.close()

tmp = open('db_sources/ncop_reports.json', 'r')
ncop_reports = simplejson.load(tmp)
tmp.close()

tmp = open('db_sources/all_bills.json', 'r')
# TODO: clean input file to avoid duplicate entries
all_bills = simplejson.load(tmp)
tmp.close()


def new_report(report_dict, tmp_bill, tmp_stage, tmp_agent, content_type):

    tmp_date = report_dict['date'][0]
    # convert date string to datetime object
    if len(tmp_date) == 10:
        tmp_date = "0" + tmp_date
    tmp_date = datetime.datetime.strptime(tmp_date, "%d %b %Y")

    tmp_link = report_dict['link'][0]
    tmp_title = report_dict['title'][0]

    event = Event()
    event.bill = tmp_bill
    event.date = tmp_date
    event.stage = tmp_stage
    event.agent = tmp_agent

    item = Content()
    item.event = event
    item.type = content_type
    item.title = tmp_title
    item.url = "http://www.pmg.org.za" + tmp_link
    #print event
    #print item
    return event, item


def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    db.drop_all()
    db.create_all()

    b1 = Bill()
    b1.name = 'Protection of State Information Bill'
    b1.code = "Bill 06"
    b1.introduced_by = "Minister of State Security"
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    db.session.add(b1)

    log = []
    for bill in all_bills:
        tmp = Bill()
        tmp.name = bill["bill_name"]
        tmp.code = bill["bill_number"]
        if bill.get("introduced_by"):
            tmp.introduced_by = bill["introduced_by"]
        unique = tmp.name + tmp.code
        while unique in log:
            tmp.code += " II"
            unique += " II"

        db.session.add(tmp)
        log.append(unique)

    location_details = [
        ("National Assembly", "NA"),
        ("National Council of Provinces", "NCOP"),
        ("The Office of the President", "President's Office"),
        ]
    locations = []

    for tmp in location_details:
        location = Location()
        location.name = tmp[0]
        location.short_name = tmp[1]
        db.session.add(location)
        locations.append(location)

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

    stage_details = [
        (locations[0], "Introduced to National Assembly", "Waiting to be assigned to a committee"),
        (locations[0], "National Assembly Committee", "Under review by National Assembly Committee"),
        (locations[0], "Public participation", "Open for public submissions"),
        (locations[0], "National Assembly", "Up for debate in the National Assembly"),
        (locations[1], "Introduced to National Council of Provinces", "Waiting to be assigned to a committee"),
        (locations[1], "National Council of Provinces Committee", "Under review by NCOP Committee"),
        (locations[1], "National Council of Provinces", "Up for debate in the NCOP"),
        (locations[0], "Mediation Committee", "Under review by Joint Committee"),
        (locations[2], "Presidential Signature", "Waiting to be signed into law"),
        ]

    stages = []
    for tmp in stage_details:
        stage = Stage()
        stage.location = tmp[0]
        stage.name = tmp[1]
        stage.default_status = tmp[2]
        db.session.add(stage)
        stages.append(stage)

    event_details = [
        (datetime.date(2010, 3, 4), stages[0], agents[5], "Introduced to parliament"),
        (datetime.date(2011, 6, 20), stages[1], agents[2], "Assigned to a committee"),
        (datetime.date(2011, 9, 4), stages[1], agents[2]),
        (datetime.date(2012, 5, 6), stages[2], agents[2]),
        (datetime.date(2013, 4, 24), stages[1], agents[2]),
        (datetime.date(2013, 5, 3), stages[1], agents[2]),
        (datetime.date(2013, 8, 20), stages[3], agents[0], "Accepted by the National Assembly"),
        (datetime.date(2013, 9, 1), stages[5], agents[3]),
        (datetime.date(2013, 9, 2), stages[6], agents[1], "Accepted by the NCOP"),
        (datetime.date(2013, 9, 3), stages[8], agents[6], "Sent back to Parliament"),
        (datetime.date(2013, 9, 4), stages[1], agents[2]),
        (datetime.date(2013, 10, 15), stages[1], agents[2]),
        ]

    events = []

    for tmp in event_details:
        event = Event()
        event.bill = b1
        event.date = tmp[0]
        event.stage = tmp[1]
        event.agent = tmp[2]
        try:
            event.new_status = tmp[3]
        except IndexError:
            event.new_status = tmp[1].default_status
        db.session.add(event)
        events.append(event)

    bill_version_details = [
        (events[0], "B6 2010", "uploads/B6-2010.pdf"),
        (events[2], "B6B 2010", "uploads/B6B-2010.pdf"),
        (events[4], "B6C 2010", "uploads/B6C-2010.pdf"),
        (events[4], "B6D 2010", "uploads/B6D-2010.pdf"),
        (events[11], "B6E 2010", "uploads/B6E-2010.pdf"),
        (events[11], "B6F 2010", "uploads/B6F-2010.pdf"),
        ]

    for tmp in bill_version_details:
        item = Version()
        item.event = tmp[0]
        item.title = tmp[1]
        item.url = tmp[2]
        db.session.add(item)

    content_type_details = [
        "gazette",
        "memorandum",
        "greenpaper",
        "whitepaper",
        "draft-bill",
        "pmg-meeting-report",
        "committee-report",
        "hansard-minutes",
        "vote-count",
        "other",
        ]

    content_types = []

    for tmp in content_type_details:
        content_type = ContentType(name=tmp)
        db.session.add(content_type)
        content_types.append(content_type)

    content_details = [
        (events[0], content_types[0], "Gazette no. 32999", "uploads/Gazette-32999_2010-03-05.pdf"),
        (events[0], content_types[3], "White Paper", "uploads/Gazette-30885_2008-03-18.pdf"),
        (events[1], content_types[5], "Meeting report: 20 June 2011", "uploads/example.pdf"),
        (events[3], content_types[5], "Meeting report: 6 May 2012 - Public Hearings", "uploads/example.pdf"),
        (events[4], content_types[6], "Committee Report", "http://www.pmg.org.za/report/20130423-protection-state-information-bill-and-committee-report-adoption"),
        (events[5], content_types[5], "Meeting report: 3 May 2013", "uploads/example.pdf"),
        (events[5], content_types[6], "Committee Report", "uploads/example.pdf"),
        (events[6], content_types[7], "Hansard Minutes", "uploads/example.pdf"),
        (events[11], content_types[6], "Committee Report", "http://www.pmg.org.za/atc131015-report-ad-hoc-committee-protection-state-information-bill-protection-state-information-bill-b-6d-2010"),
        ]

    content = []
    for tmp in content_details:
        item = Content()
        item.event = tmp[0]
        item.type = tmp[1]
        item.title = tmp[2]
        item.url = tmp[3]
        db.session.add(item)
        content.append(item)

    for na_report in na_reports:
        tmp_event, tmp_content = new_report(na_report, b1, stages[1], agents[2], content_types[-1])
        db.session.add(tmp_event)
        db.session.add(tmp_content)

    for ncop_report in ncop_reports:
        tmp_event, tmp_content = new_report(ncop_report, b1, stages[5], agents[3], content_types[-1])
        db.session.add(tmp_event)
        db.session.add(tmp_content)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()