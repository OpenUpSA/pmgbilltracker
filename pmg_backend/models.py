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

    __table_args__ = ( db.UniqueConstraint('code', 'year'), { } )
    bill_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    code = db.Column(db.String(100))
    year = db.Column(db.Integer)
    introduced_by = db.Column(db.String(500))
    bill_type = db.Column(db.String(100))
    objective = db.Column(db.String(1000))
    status = db.Column(db.String(100))

    white_paper = db.Column(db.String(200))
    green_paper = db.Column(db.String(200))
    draft = db.Column(db.String(200))
    gazette = db.Column(db.String(200))

    def to_dict(self, include_related=True):
        bill_dict = {
            c.name : getattr(self, c.name)
            for c in self.__table__.columns
        }

        if include_related:
            # add related entry objects
            entry_list = []
            if self.entries:
                latest_version = None
                current_status = None
                for entry in self.entries.order_by(Entry.date):
                    # add entry
                    entry_list.append(entry.to_dict())
                    # extract latest bill version
                    if len(entry.bill_versions.all()) > 0:
                        latest_version = entry.bill_versions[-1].to_dict()
                        bill_dict['latest_version'] = latest_version
                    # extract current status
                    if entry.new_status:
                        current_status = entry.new_status
                        bill_dict['status'] = current_status
            bill_dict['entries'] = entry_list
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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.location_id) + " - " + self.name

    def __repr__(self):
        return '<Location: %r>' % str(self)


class Stage(db.Model):

    stage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    default_status = db.Column(db.String(500))

    def to_dict(self):
        stage_dict = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
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
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

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

    stage_id = db.Column(db.Integer, db.ForeignKey('stage.stage_id'), nullable=False)
    stage = db.relationship('Stage')
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    agent = db.relationship('Agent')
    location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=False)
    location = db.relationship('Location')

    def to_dict(self):
        entry_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # nest related fields
        entry_dict.pop('agent_id')
        entry_dict['agent'] = self.agent.to_dict()
        entry_dict.pop('stage_id')
        entry_dict['stage'] = self.stage.to_dict()
        entry_dict.pop('location_id')
        entry_dict['location'] = self.location.to_dict()

        versions = []
        for item in self.bill_versions.all():
            tmp = item.to_dict()
            tmp.pop('entry_id')
            versions.append(tmp)
        entry_dict['versions'] = versions

        content = {}
        for item in self.content.all():
            tmp = item.to_dict()
            tmp.pop('entry_id')
            content_type = tmp['type']
            if content.get(content_type):
                content[content_type].append(tmp)
            else:
                content[content_type] = [tmp, ]
        entry_dict['content'] = content

        entry_dict.pop('bill_id')
        return entry_dict

    def __str__(self):
        return str(self.entry_id) + " - (" + str(self.stage) + ") " + str(self.agent)

    def __repr__(self):
        return '<Entry: %r>' % str(self)


class Tag(db.Model):

    tag_id = db.Column(db.Integer, primary_key=True)

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.bill_id'), nullable=False)
    bill = db.relationship('Bill', backref=db.backref('content', lazy='dynamic'))
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.entry_id'), nullable=False)
    entry = db.relationship('Entry', backref=db.backref('tags', lazy='dynamic'))

    def __str__(self):
        return str(self.tag_id) + " - (" + str(self.bill) + ") " + str(self.entry)

    def __repr__(self):
        return '<Entry: %r>' % str(self)