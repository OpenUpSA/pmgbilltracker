from pmg_backend import db


class Bill(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(100))
    objective = db.Column(db.String(1000))

    def __init__(self, name, type, objective):
        self.name = name
        self.type = type
        self.objective = objective

    def __repr__(self):
        return '<Bill: %r>' % self.name


class Agent(db.Model):
    agent_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Agent: %r>' % self.name


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

    def __repr__(self):
        return '<Version: %r>' % self.code