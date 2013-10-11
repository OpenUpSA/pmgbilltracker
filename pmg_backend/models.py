from pmg_backend import db


class Bill(db.Model):

    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True)
    bill_type = db.Column(db.String(100))
    objective = db.Column(db.String(1000))

    def to_dict(self, include_related=True):
        # convert table row to dictionary
        bill_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if include_related:
            # add related event objects
            event_list = []
            if self.events:
                for event in self.events:
                    event_list.append(event.to_dict())
            bill_dict['events'] = event_list
        return bill_dict

    def __str__(self):
        return str(self.bill_id) + " - " + self.name

    def __repr__(self):
        return '<Bill: %r>' % str(self)


association_table = db.Table('association', db.Base.metadata,
  db.Column('agent_id', db.Integer, db.ForeignKey('agent.agent_id')),
  db.Column('representative_id', db.Integer, db.ForeignKey('representative.representative_id'))
)


class Agent(db.Model):

    agent_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))
    role = db.relationship('Role', backref=db.backref('Agents', lazy='dynamic'))
    representatives = db.relationship("Representative", secondary=association_table, backref="agents")

    def to_dict(self):
        # convert table row to dictionary
        agent_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return agent_dict

    def __str__(self):
        return str(self.agent_id) + " - " + str(self.role.name)

    def __repr__(self):
        return '<Agent: %r>' % str(self)


class Representative(db.Model):

    representative_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    title = db.Column(db.String(100))
    gender = db.Column(db.String(1))
    political_party = db.Column(db.String(100))

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.representative_id) + " - " + " " + self.name

    def __repr__(self):
        return '<Representative: %r>' % str(self)


class Role(db.Model):

    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True)

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.role_id) + " - " + " " + self.name

    def __repr__(self):
        return '<Role: %r>' % str(self)


class Location(db.Model):

    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True)

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.location_id) + " - " + self.name

    def __repr__(self):
        return '<Location: %r>' % str(self)


class Event(db.Model):

    event_id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.bill_id'))
    bill = db.relationship('Bill', backref=db.backref('events', lazy='dynamic'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'))
    agent = db.relationship('Agent', backref=db.backref('events', lazy='dynamic'))
    resolution_id = db.Column(db.Integer, db.ForeignKey('resolution.resolution_id'))
    resolution = db.relationship('Resolution', backref=db.backref('event', uselist=False))
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'))
    session = db.relationship('Session', backref=db.backref('event', uselist=False))
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.revision_id'))
    revision = db.relationship('Revision', backref=db.backref('event', uselist=False))

    date = db.Column(db.Date)

    def to_dict(self):
        # convert table row to dictionary
        event_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # nest related fields
        event_dict.pop('agent_id')
        event_dict['agent'] = self.agent.to_dict()

        content = []
        for item in self.content.all():
            tmp = item.to_dict()
            tmp.pop('event_id')
            content.append(tmp)
        event_dict['content'] = content

        event_dict.pop('bill_id')
        return event_dict

    def __str__(self):
        return str(self.event_id) + " - (" + self.location + ") " + self.agent

    def __repr__(self):
        return '<Event: %r>' % str(self)


class Resolution(db.Model):

    resolution_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), unique=True)
    outcome = db.Column(db.Boolean)
    count_for = db.Column(db.Integer)
    count_against = db.Column(db.Integer)

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.resolution_id) + " - (" + self.type + ") " + str(self.outcome)

    def __repr__(self):
        return '<Resolution: %r>' % str(self)


class Session(db.Model):

    session_id = db.Column(db.Integer, primary_key=True)
    date_end = db.Column(db.Date)
    minutes = db.Column(db.String(500))
    report = db.Column(db.String(500))

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.session_id) + " - " + self.date

    def __repr__(self):
        return '<Session: %r>' % str(self)


class Revision(db.Model):

    revision_id = db.Column(db.Integer, primary_key=True)

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.revision_id)

    def __repr__(self):
        return '<Revision: %r>' % str(self)


class Version(db.Model):

    version_id = db.Column(db.Integer, primary_key=True)
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.revision_id'))
    revision = db.relationship('Revision', backref=db.backref('versions', lazy='dynamic'))
    name = db.Column(db.String(500))
    url = db.Column(db.String(500))

    def to_dict(self):
        # convert table row to dictionary
        version_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return version_dict

    def __str__(self):
        return str(self.version_id) + " - " + " " + self.name

    def __repr__(self):
        return '<Version: %r>' % str(self)


class Content(db.Model):

    content_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    event = db.relationship('Event', backref=db.backref('content', lazy='dynamic'))

    type = db.Column(db.String(100))
    title = db.Column(db.String(500))
    description = db.Column(db.String(1000))
    url = db.Column(db.String(500))

    def to_dict(self):
        # convert table row to dictionary
        content_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return content_dict

    def __str__(self):
        return str(self.content_id) + " - (" + self.type + ") " + self.title

    def __repr__(self):
        return '<Content: %r>' % str(self)