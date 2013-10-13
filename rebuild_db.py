import datetime
def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    from pmg_backend import db
    db.drop_all()
    db.create_all()

    from pmg_backend.models import Bill, Agent, Location, Stage, Event, Content, Resolution, Revision, Session

    b1 = Bill()
    b1.name = 'Protection of State Information Bill'
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    db.session.add(b1)

    locations = [
        "National Assembly (NA)",
        "National Council of Provinces (NCOP)",
        "The Office of the President",
    ]

    for tmp in locations:
        location = Location()
        location.name = tmp
        db.session.add(location)

    agents = [
        "National Assembly (NA)",
        "NA Committee",
        "National Council of Provinces (NCOP)",
        "NCOP Committee",
        "Joint Committee",
        "Minister",
        "President",
        "Member of Parliament",
    ]

    for tmp in agents:
        agent = Agent()
        agent.name = tmp
        db.session.add(agent)

    stages = [
        "Waiting to be introduced to National Assembly",
        "Introduced to National Assembly",
        "Assigned to National Assembly Committee",
        "Being reviewed by National Assembly Committee",
        "Awaiting vote in National Assembly",
        "Waiting to be introduced to National Council of Provinces"
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

    content = [
        ("memorandum", "Explanatory Memorandum", "uploads/memo-1.html"),
        ("greenpaper", "Green Paper", "uploads/greenpaper.pdf"),
        ("whitepaper", "White Paper", "uploads/whitepaper.pdf"),
        ("draft", "Draft Bill", "uploads/draft.pdf"),
        ("pmg-meeting-report", "Meeting report: 3 May 2013", "uploads/pmg-report-1.pdf"),
        ("pmg-meeting-report", "Meeting report: 6 May 2012 - Public Hearings", "uploads/pmg-report-2.pdf"),
        ("pmg-meeting-report", "Meeting report: 20 June 2011", "uploads/pmg-report-1.pdf"),
        ("committee-report", "Committee Report", "uploads/committee-report-1.pdf"),
        ("hansard-minutes", "Hansard Minutes", "uploads/hansard-1.pdf"),
    ]

    for tmp in content:
        item = Content()
        item.type = tmp[0]
        item.title = tmp[1]
        item.url = tmp[2]
        db.session.add(item)

    revisions = [
        ('B6 2010', 'uploads/revision-1.pdf'),
        ('B6B 2010', 'uploads/revision-2.pdf'),
        ('B6C 2010', 'uploads/revision-3.pdf'),
        ('B6D 2010', 'uploads/revision-4.pdf'),
    ]

    for tmp in revisions:
        revision = Revision()
        revision.name = tmp[0]
        revision.url = tmp[1]
        db.session.add(revision)

    sessions = [
        (datetime.date(2011, 6, 20), ),
        (datetime.date(2012, 5, 6), ),
        (datetime.date(2013, 5, 3), ),
        (datetime.date(2013, 8, 20), ),
    ]

    for tmp in sessions:
        item = Session()
        item.date_end= tmp[0]
        db.session.add(item)

    resolutions = [
        ("vote", "pass", 235, 85, 2),
        ("vote", "pass", None, None, None),
        ("signing", "fail", 235, 85, 2),
    ]

    for tmp in resolutions:
        resolution = Resolution()
        resolution.type = tmp[0]
        resolution.outcome = tmp[1]
        resolution.count_for = tmp[2]
        resolution.count_against = tmp[3]
        resolution.count_abstain = tmp[4]
        db.session.add(resolution)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()