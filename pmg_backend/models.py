from pmg_backend import db


class Bill(db.Model):

    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
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


class Agent(db.Model):

    agent_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def to_dict(self):
        # convert table row to dictionary
        agent_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return agent_dict

    def __str__(self):
        return str(self.agent_id) + " - " + self.name

    def __repr__(self):
        return '<Agent: %r>' % str(self)


class Version(db.Model):

    version_id = db.Column(db.Integer, primary_key=True)

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.bill_id'))
    bill = db.relationship('Bill', backref=db.backref('versions', lazy='dynamic'))

    code = db.Column(db.String(100), unique=True)
    date_released = db.Column(db.Date)
    url = db.Column(db.String(500))

    def to_dict(self):
        # convert table row to dictionary
        version_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return version_dict

    def __str__(self):
        return str(self.version_id) + " - " + str(self.bill.name) + " " + self.code

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

    def to_dict(self):
        # convert table row to dictionary
        event_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # nest related fields
        event_dict.pop('agent_id')
        event_dict['agent'] = self.agent.to_dict()
        event_dict.pop('version_id')
        event_dict['version'] = self.new_version.to_dict()

        supporting_content = []
        for content in self.supporting_content.all():
            tmp = content.to_dict()
            tmp.pop('event_id')
            supporting_content.append(tmp)
        event_dict['supporting_content'] = supporting_content

        event_dict.pop('bill_id')
        return event_dict

    def __str__(self):
        return str(self.event_id) + " - (" + self.event_type + ") " + self.new_status

    def __repr__(self):
        return '<Event: %r>' % str(self)


class SupportingContent(db.Model):

    supporting_content_id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    event = db.relationship('Event', backref=db.backref('supporting_content', lazy='dynamic'))

    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    url = db.Column(db.String(500))

    def to_dict(self):
        # convert table row to dictionary
        content_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return content_dict

    def __str__(self):
        return str(self.supporting_content_id) + " - " + self.title

    def __repr__(self):
        return '<Supporting Content: %r>' % str(self)