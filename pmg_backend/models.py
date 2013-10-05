from pmg_backend import db
from datetime import datetime


class Bill(db.Model):

    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(100))
    objective = db.Column(db.String(1000))

    def __init__(self, name, type, objective):
        self.name = name
        self.type = type
        self.objective = objective

    def to_dict(self):
        # convert table row to dictionary
        bill_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # add related event objects
        event_list = []
        if self.events:
            for event in self.events:
                event_list.append(event.to_dict())
        bill_dict['events'] = event_list
        return bill_dict

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Bill: %r>' % str(self)


class Agent(db.Model):

    agent_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Agent: %r>' % str(self)


class Version(db.Model):

    version_id = db.Column(db.Integer, primary_key=True)

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.bill_id'))
    bill = db.relationship('Bill', backref=db.backref('versions', lazy='dynamic'))

    code = db.Column(db.String(100), unique=True)
    date_released = db.Column(db.Date)
    url = db.Column(db.String(500))

    def __init__(self, bill, code, url, date_released=None):
        self.bill = bill
        self.code = code
        self.url = url
        self.date_released = date_released

    def __str__(self):
        return self.code

    def __repr__(self):
        return '<Version: %r>' % str(self)


class Event(db.Model):

    event_id = db.Column(db.Integer, primary_key=True)

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.bill_id'))
    bill = db.relationship('Bill', backref=db.backref('events', lazy='dynamic'))

    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'))
    agent = db.relationship('Agent', backref=db.backref('events', lazy='dynamic'))

    event_type = db.Column(db.String(100), unique=True)
    new_status = db.Column(db.String(100))
    version_id = db.Column(db.Integer, db.ForeignKey('version.version_id'))
    new_version = db.relationship('Version', backref=db.backref('event', lazy='dynamic'))

    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)

    def __init__(self, bill, agent, event_type, new_status=None, new_version=None, date_start=None, date_end=None):
        self.bill = bill
        self.agent = agent
        self.event_type = event_type
        if new_status:
            self.new_status = new_status
        if new_version:
            self.new_version = new_version
        if date_start:
            self.date_start = date_start
        else:
            self.date_start = datetime.now()
        if date_end:
            self.date_end = date_end
        else:
            self.date_end = datetime.now()

    def to_dict(self):
        # convert table row to dictionary
        event_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # add related fields
        event_dict['agent'] = self.agent
        event_dict['version'] = self.new_version
        return event_dict

    def __str__(self):
        return self.event_type + " - " + self.new_status

    def __repr__(self):
        return '<Event: %r>' % str(self)


class SupportingContent(db.Model):

    supporting_content_id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    event = db.relationship('Event', backref=db.backref('supporting_content', lazy='dynamic'))

    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    url = db.Column(db.String(500))

    def __init__(self, event, title, description, url):
        self.event = event
        self.title = title
        self.description = description
        self.url = url

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Supporting Content: %r>' % str(self)