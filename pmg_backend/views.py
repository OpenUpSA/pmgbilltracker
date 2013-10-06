from flask import request, url_for, session, render_template
from pmg_backend import app
import requests
import simplejson
from datetime import datetime, date
import logging
from models import *
from pmg_backend import db


class CustomEncoder(simplejson.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            encoded_obj = str(obj)
        else:
            encoded_obj = simplejson.JSONEncoder.default(self, obj)
        return encoded_obj


@app.route('/')
def autodiscover():
    bills = Bill.query.all()
    agents = Agent.query.all()
    versions = Version.query.all()
    events = Event.query.all()
    supporting_content = SupportingContent.query.all()

    return render_template('index.html', models=[bills, agents, versions, events, supporting_content])


@app.route('/bill/')
@app.route('/bill/<bill_id>/')
def bill(bill_id=None):

    if bill_id:
        bill_obj = Bill.query.get_or_404(bill_id)
        out = bill_obj.to_dict()

    else:
        out = []
        bill_set = Bill.query.all()
        for bill_obj in bill_set:
            out.append(bill_obj.to_dict())

    return simplejson.dumps(out, cls=CustomEncoder)