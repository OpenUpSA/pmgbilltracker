def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    from pmg_backend import db
    db.drop_all()
    db.create_all()

    from pmg_backend.models import Bill, Agent, Version, Event, SupportingContent

    b1 = Bill('Test Bill', 'Section 75', 'The aim of this bill is to demonstrate the functionality of the PMG billtracker application.')
    db.session.add(b1)

    a1 = Agent('National Assembly')
    a2 = Agent('National Council of Provinces')
    a3 = Agent('Ad-Hoc committee on the Develpment of Applications.')
    a4 = Agent('Minister of Application Development')
    db.session.add(a1)
    db.session.add(a2)
    db.session.add(a3)
    db.session.add(a4)

    v1 = Version(b1, 'B1 2012', 'http://example.com')
    v2 = Version(b1, 'B2 2012', 'http://example.com')
    db.session.add(v1)
    db.session.add(v2)

    e1 = Event(b1, a4, "A", "Introduced to Parliament", v1)
    db.session.add(e1)

    c1 = SupportingContent(e1, "Explanatory memorandum", "This is a brief description of the document.", "http://example.com")
    db.session.add(c1)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()