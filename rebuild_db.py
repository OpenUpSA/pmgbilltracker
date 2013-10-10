def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    from pmg_backend import db
    db.drop_all()
    db.create_all()

    from pmg_backend.models import *

    b1 = Bill()
    b1.name = 'Test Bill'
    b1.bill_type = 'Section 75'
    b1.objective = 'The aim of this bill is to demonstrate the functionality of the PMG Bill Tracker application.'
    db.session.add(b1)

    a1 = Agent()
    a1.name = 'National Assembly'
    a2 = Agent()
    a2.name = 'National Council of Provinces'
    a3 = Agent()
    a3.name = 'Ad-Hoc committee on the Develpment of Applications.'
    a4 = Agent()
    a4.name = 'Minister of Application Development'
    db.session.add(a1)
    db.session.add(a2)
    db.session.add(a3)
    db.session.add(a4)

    v1 = Version()
    v1.bill = b1
    v1.code = 'B1 2012'
    v1.url = 'http://example.com'
    v2 = Version()
    v2.bill = b1
    v2.code = 'B2 2012'
    v2.url = 'http://example.com'
    db.session.add(v1)
    db.session.add(v2)

    e1 = Event()
    e1.bill = b1
    e1.agent = a4
    e1.event_type = "A"
    e1.new_status = "Introduced to Parliament"
    e1.new_version = v1
    db.session.add(e1)

    c1 = SupportingContent()
    c1.event = e1
    c1.title = "Explanatory memorandum"
    c1.description = "This is a brief description of the document."
    c1.url = "http://example.com"
    db.session.add(c1)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()