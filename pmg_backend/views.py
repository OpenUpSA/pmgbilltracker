from flask import request, url_for, session
from pmg_backend import app
import requests
import simplejson
import logging
from models import Bill, Agent, Version, Event, SupportingContent

@app.route('/')
def hello_world():

    out = "<h1>Current models</h1>"

    bills = Bill.query.all()
    agents = Agent.query.all()
    versions = Version.query.all()
    events = Event.query.all()
    supporting_content = SupportingContent.query.all()

    for queryset in [bills, agents, versions, events, supporting_content]:
        out += "<h2>" + str(queryset[0])[1:-1].split(":")[0] + "</h2>"
        for obj in queryset:
            out += str(obj)[1:-1] + "<br>"

    return out