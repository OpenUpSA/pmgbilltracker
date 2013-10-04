from flask import request, url_for, session
from pmg_backend import app
import requests
import simplejson
import logging
from models import User

@app.route('/')
def hello_world():
    out = ""
    tmp = User.query.all()
    for user in tmp:
        out += user.email + "<br>"
    return out

if __name__ == '__main__':
    app.run()