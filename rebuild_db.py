import datetime

def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    from pmg_backend import db
    db.drop_all()
    db.create_all()

    from pmg_backend.models import Bill, Agent, Location, Stage, Event, Content, Resolution

    b1 = Bill()
    b1.name = 'Protection of State Information Bill'
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    b1.gazette = '32999'
    db.session.add(b1)

    location_names = [
        "National Assembly (NA)",
        "National Council of Provinces (NCOP)",
        "The Office of the President",
    ]
    locations = []

    for tmp in location_names:
        location = Location()
        location.name = tmp
        locations.append(location)

    agents = [
        ("House of Parliament", "National Assembly (NA)"),
        ("House of Parliament", "National Council of Provinces (NCOP)"),
        ("NA Committee", "Ad Hoc Committee on Protection of State Information Bill"),
        ("NCOP Committee", "Unnamed"),
        ("Joint Committee", "Unnamed"),
        ("Minister", "Minister of State Security"),
        ("President", "The President of the Republic of South Africa"),
        ("Member of Parliament", "Unnamed"),
    ]

    for tmp in agents:
        agent = Agent()
        agent.type = tmp[0]
        agent.name = tmp[1]
        db.session.add(agent)

    stages = [
        "Waiting to be introduced to National Assembly",
        "Introduced to National Assembly",
        "Assigned to National Assembly Committee",
        "Being reviewed by National Assembly Committee",
        "Undergoing public hearings",
        "Awaiting vote in National Assembly",
        "Second Reading in National Assembly",
        "Waiting to be introduced to National Council of Provinces",
        "Introduced to National Council of Provinces",
        "Assigned to NCOP Committee",
        "Being reviewed by NCOP Committee",
        "Awaiting vote in National Council of Provinces",
        "Assigned to Mediation committee",
        "Dropped",
        "Waiting to be signed into law",
        "Signed into law",
    ]

    for tmp in stages:
        stage = Stage()
        stage.name = tmp
        db.session.add(stage)

    event_dates = [
        (datetime.date(2010, 3, 4), locations[0]),
        (datetime.date(2011, 6, 20), locations[0]),
        (datetime.date(2011, 9, 4), locations[0]),
        (datetime.date(2012, 5, 6), locations[0]),
        (datetime.date(2013, 4, 24), locations[0]),
        (datetime.date(2013, 5, 3), locations[0]),
        (datetime.date(2013, 8, 20), locations[0]),
        (datetime.date(2013, 9, 1), locations[1]),
        (datetime.date(2013, 9, 2), locations[1]),
        (datetime.date(2013, 9, 3), locations[2]),
        (datetime.date(2013, 9, 4), locations[0]),
    ]

    events = []

    for tmp in event_dates:
        event = Event()
        event.bill = b1
        event.date = tmp[0]
        event.location = tmp[1]
        events.append(event)

    content = [
        (events[0], "revision", "B6 2010", "uploads/revision-1.pdf"),
        (events[2], "revision", "B6B 2010", "uploads/revision-2.pdf"),
        (events[4], "revision", "B6C 2010", "uploads/revision-3.pdf"),
        (events[4], "revision", "B6D 2010", "uploads/revision-4.pdf"),
        (events[0], "memorandum", "Explanatory Memorandum", "uploads/memo-1.html"),
        (events[0], "greenpaper", "Green Paper", "uploads/greenpaper.pdf"),
        (events[0], "whitepaper", "White Paper", "uploads/whitepaper.pdf"),
        (events[0], "draft", "Draft Bill", "uploads/draft.pdf"),
        (events[1], "pmg-meeting-report", "Meeting report: 20 June 2011", "uploads/pmg-report-1.pdf"),
        (events[3], "pmg-meeting-report", "Meeting report: 6 May 2012 - Public Hearings", "uploads/pmg-report-2.pdf"),
        (events[5], "pmg-meeting-report", "Meeting report: 3 May 2013", "uploads/pmg-report-1.pdf"),
        (events[5], "committee-report", "Committee Report", "uploads/committee-report-1.pdf"),
        (events[6], "hansard-minutes", "Hansard Minutes", "uploads/hansard-1.pdf"),
    ]

    for tmp in content:
        item = Content()
        item.event = tmp[0]
        item.type = tmp[1]
        item.title = tmp[2]
        item.url = tmp[3]
        db.session.add(item)

    resolutions = [
        (events[6], "vote", "pass", 235, 85, 2),
        (events[8], "vote", "pass", None, None, None),
        (events[9], "signing", "fail", 235, 85, 2),
    ]

    for tmp in resolutions:
        resolution = Resolution()
        resolution.event = tmp[0]
        resolution.type = tmp[1]
        resolution.outcome = tmp[2]
        resolution.count_for = tmp[3]
        resolution.count_against = tmp[4]
        resolution.count_abstain = tmp[5]
        db.session.add(resolution)

    for location in locations:
        db.session.add(location)

    for event in events:
        db.session.add(event)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()