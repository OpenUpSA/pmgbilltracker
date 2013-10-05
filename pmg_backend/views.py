from flask import request, url_for, session
from pmg_backend import app
import requests
import simplejson
import logging
from models import Bill, Agent, Version

@app.route('/')
def hello_world():

    out = "<h1>Current models</h1>"

    bills = Bill.query.all()
    out += "<h2>BILL</h2>"
    for bill in bills:
        out += bill.name + "<br>"

    agents = Agent.query.all()
    out += "<h2>AGENT</h2>"
    for agent in agents:
        out += agent.name + "<br>"

    versions = Version.query.all()
    out += "<h2>VERSION</h2>"
    for version in versions:
        out += version.code + "<br>"

    return out