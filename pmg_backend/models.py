from pmg_backend import db
from sqlalchemy.orm import backref

class classproperty(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))

    is_active = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def delete(self):
        self.is_active = False
        self.is_deleted = False

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_active

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.username


# M2M table
entry_bills_table = db.Table(
    'entry_bills', db.Model.metadata,
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.entry_id')),
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.bill_id'))
)


class Bill(db.Model):

    __table_args__ = (db.UniqueConstraint('code', 'year', 'name'), {})
    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    code = db.Column(db.String(100))
    bill_type = db.Column(db.String(100))
    year = db.Column(db.Integer)
    number = db.Column(db.Integer)

    objective = db.Column(db.String(1000))
    status = db.Column(db.String(100))

    is_deleted = db.Column(db.Boolean, default=False)

    def delete(self):
        self.is_deleted = True

    @classproperty
    def regular_bills(cls):
        return cls.query.filter(Bill.bill_type=="B")

    @classproperty
    def pmb(cls):
        return cls.query.filter(Bill.bill_type=="PMB")

    @classproperty
    def draft_bills(cls):
        # TODO: set "draft" as a special bill_type
        return cls.query.filter(Bill.code==None)

    @classproperty
    def current_bills(cls):
        return cls.query\
            .filter(Bill.status != "enacted")\
            .filter(Bill.status != "withdrawn")\
            .filter(Bill.status != "expired")\
            .filter(Bill.status != None)

    def __str__(self):
        return str(self.bill_id) + " - " + self.name

    def __repr__(self):
        return '<Bill: %r>' % str(self)


class Agent(db.Model):

    agent_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(500))
    name = db.Column(db.String(500))
    url = db.Column(db.String(500))
    location = db.Column(db.Integer)

    is_deleted = db.Column(db.Boolean, default=False)

    def delete(self):
        self.is_deleted = True

    def __str__(self):
        tmp = "(" + self.type + ")"
        if self.name:
            tmp = self.name + " " + tmp
        return tmp

    def __repr__(self):
        return '<Agent: %r>' % str(self)


class Entry(db.Model):

    entry_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500))
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(1000))
    location = db.Column(db.Integer, nullable=True)

    is_deleted = db.Column(db.Boolean, default=False)

    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=True)
    agent = db.relationship('Agent')
    bills = db.relationship('Bill', secondary=entry_bills_table, backref=backref("entries", order_by=(date, title)))

    def delete(self):
        self.is_deleted = True

    def __str__(self):
        return str(self.entry_id) + " - " + self.title

    def __repr__(self):
        return '<Entry: %r>' % str(self)
