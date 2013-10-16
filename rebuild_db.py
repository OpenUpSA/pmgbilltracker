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
    b1.status = 'Sent back to Parliament by the President'
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    db.session.add(b1)

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
        (locations[1], "National Council of Provinces Committee", "Under review by National Council of Provinces Committee"),
        (locations[1], "National Council of Provinces", "Up for debate in the National Council of Provinces"),
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
        (datetime.date(2010, 3, 4), stages[0], agents[5]),
        (datetime.date(2011, 6, 20), stages[1], agents[2]),
        (datetime.date(2011, 9, 4), stages[1], agents[2]),
        (datetime.date(2012, 5, 6), stages[2], agents[2]),
        (datetime.date(2013, 4, 24), stages[1], agents[2]),
        (datetime.date(2013, 5, 3), stages[1], agents[2]),
        (datetime.date(2013, 8, 20), stages[3], agents[0]),
        (datetime.date(2013, 9, 1), stages[5], agents[3]),
        (datetime.date(2013, 9, 2), stages[6], agents[1]),
        (datetime.date(2013, 9, 3), stages[8], agents[6]),
        (datetime.date(2013, 9, 4), stages[1], agents[2]),
        ]

    events = []

    for tmp in event_details:
        event = Event()
        event.bill = b1
        event.date = tmp[0]
        event.stage = tmp[1]
        event.agent = tmp[2]
        db.session.add(event)
        events.append(event)

    content_details = [
        (events[0], "gazette", "32999", "uploads/gazette-1.pdf"),
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

    content = []
    for tmp in content_details:
        item = Content()
        item.event = tmp[0]
        item.type = tmp[1]
        item.title = tmp[2]
        item.url = tmp[3]
        db.session.add(item)
        content.append(item)

    resolution_details = [
        (events[6], "vote", "pass", 235, 85, 2),
        (events[8], "vote", "pass", None, None, None),
        (events[9], "signing", "fail", 235, 85, 2),
        ]

    resolutions = []
    for tmp in resolution_details:
        resolution = Resolution()
        resolution.event = tmp[0]
        resolution.type = tmp[1]
        resolution.outcome = tmp[2]
        resolution.count_for = tmp[3]
        resolution.count_against = tmp[4]
        resolution.count_abstain = tmp[5]
        db.session.add(resolution)
        resolutions.append(resolution)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()