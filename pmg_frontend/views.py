from flask import request, make_response, url_for, session, render_template, abort
from pmg_frontend import app
import requests
import simplejson
from datetime import datetime, date
from pmg_frontend import logger


API_HOST = app.config['API_HOST']

@app.route('/')
def index():
    """
    Display a list of available bills, with some summary info and a link to each bill's detail page.
    """

    logger.debug("landing page called")
    r = requests.get("http://" + API_HOST + "/bill/")
    bills = r.json()

    return render_template('index.html', bills=bills)


@app.route('/bill/<bill_id>/')
def detail(bill_id=None):
    """
    Display all available detail for the requested bill.
    """

    try:
        bill_id = int(bill_id)
    except:
        abort(400)

    logger.debug("detail page called")
    r = requests.get("http://" + API_HOST + "/bill/" + str(bill_id) + "/")
    bill = r.json()

    return render_template('detail.html', bill=bill)