from pmg_backend import db


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


class Bill(db.Model):

    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True, nullable=False)
    status = db.Column(db.String(500))
    bill_type = db.Column(db.String(100))
    objective = db.Column(db.String(1000))

    def to_dict(self, include_related=True):
        # convert table row to dictionary
        bill_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        if include_related:
            # add related event objects
            event_list = []
            if self.events:
                for event in self.events.order_by(Event.date.desc()):
                    event_list.append(event.to_dict())
            bill_dict['events'] = event_list
        return bill_dict

    def __str__(self):
        return str(self.bill_id) + " - " + self.name

    def __repr__(self):
        return '<Bill: %r>' % str(self)


class Location(db.Model):

    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True, nullable=False)
    short_name = db.Column(db.String(100))

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.location_id) + " - " + self.name

    def __repr__(self):
        return '<Location: %r>' % str(self)


class Stage(db.Model):

    stage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    default_status = db.Column(db.String(500))

    location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=False)
    location = db.relationship('Location')

    def to_dict(self):
        # convert table row to dictionary
        stage_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        stage_dict.pop('location_id')
        stage_dict['location'] = self.location.to_dict()
        return stage_dict

    def __str__(self):
        return str(self.stage_id) + " - " + self.name

    def __repr__(self):
        return '<Stage: %r>' % str(self)


class Agent(db.Model):

    agent_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(500))
    name = db.Column(db.String(500))
    short_name = db.Column(db.String(100))
    url = db.Column(db.String(500))

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        tmp = str(self.agent_id) + " - (" + self.type + ")"
        if self.name:
            tmp += " " + self.name
        return tmp

    def __repr__(self):
        return '<Agent: %r>' % str(self)


class Event(db.Model):

    event_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    new_status = db.Column(db.String(500))

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.bill_id'), nullable=False)
    bill = db.relationship('Bill')
    stage_id = db.Column(db.Integer, db.ForeignKey('stage.stage_id'), nullable=False)
    stage = db.relationship('Stage')
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    agent = db.relationship('Agent')

    def to_dict(self):
        # convert table row to dictionary
        event_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # nest related fields
        event_dict.pop('agent_id')
        event_dict['agent'] = self.agent.to_dict()
        event_dict.pop('stage_id')
        event_dict['stage'] = self.stage.to_dict()

        content = []
        for item in self.content.all():
            tmp = item.to_dict()
            tmp.pop('event_id')
            content.append(tmp)
        event_dict['content'] = content

        event_dict.pop('bill_id')
        return event_dict

    def __str__(self):
        return str(self.event_id) + " - (" + str(self.stage) + ") " + str(self.agent)

    def __repr__(self):
        return '<Event: %r>' % str(self)


class Content(db.Model):

    content_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    description = db.Column(db.String(1000))
    url = db.Column(db.String(500))

    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    event = db.relationship('Event', backref=db.backref('content', lazy='dynamic'))
    type_id = db.Column(db.Integer, db.ForeignKey('content_type.content_type_id'), nullable=False)
    type = db.relationship('ContentType')

    def to_dict(self):
        # convert table row to dictionary
        content_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        # add related content
        content_dict.pop('type_id')
        content_dict['type'] = self.type.name

        return content_dict

    def __str__(self):
        return str(self.content_id) + " - (" + self.type.name + ") " + self.title

    def __repr__(self):
        return '<Content: %r>' % str(self)


class ContentType(db.Model):

    content_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def to_dict(self):
        # convert table row to dictionary
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<Content_type: %r>' % str(self)