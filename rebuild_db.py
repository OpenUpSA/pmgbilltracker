import datetime

def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    from pmg_backend import db
    db.drop_all()
    db.create_all()

    from pmg_backend.models import Bill, Agent, Location, Stage, Event, Version, Content, ContentType

    b1 = Bill()
    b1.name = 'Protection of State Information Bill'
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    db.session.add(b1)

    b2 = Bill()
    b2.name = 'Example Bill'
    b2.bill_type = "Section 76 (Ordinary Bills affecting the provinces)"
    b2.objective = "To demonstrate the efficacy of the PMG bill-tracking application."
    db.session.add(b2)

    b3 = Bill()
    b3.name = 'Another Example Bill'
    b3.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b3.objective = "To go yet further in demonstrating the efficacy of the PMG bill-tracking application."
    db.session.add(b3)

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
        ("ncop-committee", None, None),
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
        (events[4], "B6C 2010", "uploads/B6E-2010_15Oct2013.pdf"),
        (events[4], "B6D 2010", "uploads/B6F-2010_15Oct2013.pdf"),
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
    ]

    content_types = []

    for tmp in content_type_details:
        content_type = ContentType(name=tmp)
        db.session.add(content_type)
        content_types.append(content_type)

    content_details = [
        (events[0], content_types[0], "Gazette no. 32999", "uploads/example.pdf"),
        (events[0], content_types[1], "Explanatory Memorandum", "uploads/example.pdf"),
        (events[0], content_types[2], "Green Paper", "uploads/example.pdf"),
        (events[0], content_types[3], "White Paper", "uploads/example.pdf"),
        (events[0], content_types[4], "Draft Bill", "uploads/example.pdf"),
        (events[1], content_types[5], "Meeting report: 20 June 2011", "uploads/example.pdf"),
        (events[3], content_types[5], "Meeting report: 6 May 2012 - Public Hearings", "uploads/example.pdf"),
        (events[5], content_types[5], "Meeting report: 3 May 2013", "uploads/example.pdf"),
        (events[5], content_types[6], "Committee Report", "uploads/example.pdf"),
        (events[6], content_types[7], "Hansard Minutes", "uploads/example.pdf"),
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

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()