from pmg_backend import db
from sqlalchemy.orm import backref

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.username


# M2M table
entry_bills_table = db.Table('entry_bills', db.Model.metadata,
                             db.Column('entry_id', db.Integer, db.ForeignKey('entry.entry_id')),
                             db.Column('bill_id', db.Integer, db.ForeignKey('bill.bill_id'))
)


class Bill(db.Model):

    __table_args__ = ( db.UniqueConstraint('code', 'year'), { } )
    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    code = db.Column(db.String(100))
    year = db.Column(db.Integer)
    introduced_by = db.Column(db.String(500))
    bill_type = db.Column(db.String(100))
    objective = db.Column(db.String(1000))

    white_paper = db.Column(db.String(200))
    green_paper = db.Column(db.String(200))
    draft = db.Column(db.String(200))
    gazette = db.Column(db.String(200))

    def __str__(self):
        return str(self.bill_id) + " - " + self.name

    def __repr__(self):
        return '<Bill: %r>' % str(self)


class Location(db.Model):

    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True, nullable=False)
    short_name = db.Column(db.String(100))

    def __str__(self):
        return str(self.location_id) + " - " + self.name

    def __repr__(self):
        return '<Location: %r>' % str(self)


class Status(db.Model):

    status_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), unique=True, nullable=False)

    def __str__(self):
        return str(self.status_id) + " - " + self.description

    def __repr__(self):
        return '<Status: %r>' % str(self)


class Stage(db.Model):

    stage_id = db.Column(db.Integer, primary_key=True)

    location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=True)
    location = db.relationship('Location')
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'), nullable=True)
    status = db.relationship('Status')

    def __str__(self):
        return str(self.stage_id) + " - " + self.location.name + " " + self.status.description

    def __repr__(self):
        return '<Stage: %r>' % str(self)


class Agent(db.Model):

    agent_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(500))
    name = db.Column(db.String(500))
    short_name = db.Column(db.String(100))
    url = db.Column(db.String(500))

    def __str__(self):
        tmp = str(self.agent_id) + " - (" + self.type + ")"
        if self.name:
            tmp += " " + self.name
        return tmp

    def __repr__(self):
        return '<Agent: %r>' % str(self)


class Entry(db.Model):

    entry_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)

    type = db.Column(db.String(100))
    url = db.Column(db.String(500))
    title = db.Column(db.String(500))
    description = db.Column(db.String(1000))

    stage_id = db.Column(db.Integer, db.ForeignKey('stage.stage_id'), nullable=True)
    stage = db.relationship('Stage')
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=True)
    agent = db.relationship('Agent')
    bills = db.relationship('Bill', secondary=entry_bills_table, backref=backref("entries", order_by=date))

    def __str__(self):
        return str(self.entry_id) + " - (" + str(self.stage) + ") " + str(self.agent)

    def __repr__(self):
        return '<Entry: %r>' % str(self)