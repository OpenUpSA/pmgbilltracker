from flask import request, make_response, url_for, session, render_template, abort, redirect
from pmg_frontend import app
import requests
import simplejson
from datetime import datetime, date
from pmg_frontend import logger


API_HOST = app.config['API_HOST']
error_bad_request = 400

def url(action, param=None):
    u =  "http://{host}/{action}/".format(host=API_HOST, action=action)
    if param:
        return u + param + "/"
    return u

@app.route('/')
def root():
    return redirect('/bills/')

@app.route('/bills/all/')
@app.route('/bills/<year>/')
@app.route('/bills/<bill_type>/all/')
@app.route('/bills/<bill_type>/<year>/')
def index(year=None, bill_type=None):
    """
    Display a list of available bills, with some summary info and a link to each bill's detail page.
    """

    logger.debug("landing page called")
    try:
        if year is not None:
            year = int(year)
    except ValueError as e:
        logger.debug(e)
        abort(error_bad_request)

    start_year = date.today().year
    if not year:
        year = start_year

    tmp = "bill"
    page_title = "All bills"
    bills = []

    while (not bills) and (start_year > 2007):  # ensure that we start on the first page that actually has content
        year_list = range(start_year, 2005, -1)

        if bill_type and bill_type.lower() in ["pmb", "draft", "current"]:
            tmp = bill_type.lower()
            if bill_type.lower() == "pmb":
                page_title = "Private Member Bills"
                year_list = range(start_year, 2011, -1)
            elif bill_type.lower() == "draft":
                page_title = "Draft Bills"
                year_list = range(start_year, 2007, -1)
            elif bill_type.lower() == "current":
                page_title = "Current Bills"
                start_year = None
                year = None
                year_list = []

        api_url = url(tmp)

        if year:
            r = requests.get(api_url + "year/" + str(year) + "/")
        else:
            r = requests.get(api_url)
        bills = r.json()
        if not bills and bill_type.lower() != "current":
            start_year -= 1
            year -= 1

    status_dict = {
        "na": ("in progress", "label-primary"),
        "ncop": ("in progress", "label-primary"),
        "assent": ("submitted to the president", "label-warning"),
        "enacted": ("signed into law", "label-success"),
        "withdrawn": ("withdrawn", "label-default"),
        }

    return render_template(
        'index.html', title=page_title, bill_type=bill_type, year_list=year_list,
        year=year, bills=bills, status_dict=status_dict, api_url=api_url
    )


@app.route('/bills/')
def bills():

    return render_template('bills.html')


@app.route('/bills/explained/')
def bills_explained():

    return render_template('bills_explained.html')


@app.route('/bill/<bill_id>/')
def detail(bill_id=None):
    """
    Display all available detail for the requested bill.
    """

    try:
        bill_id = int(bill_id)
    except:
        abort(error_bad_request)

    logger.debug("detail page called")
    api_url = url("bill", str(bill_id))
    r = requests.get(api_url)
    bill = r.json()

    entries = bill["entries"]

    # separate special entries from the rest of the list
    version_types = ["bill-version", "act"]
    special_types = ["gazette", "whitepaper", "memorandum", "greenpaper", "draft"]

    bill["entries"] = [entry for entry in entries if entry["type"] not in version_types + special_types]

    bill["versions"] = [entry for entry in entries if entry["type"] in version_types]
    special_entries = [entry for entry in entries if entry["type"] in special_types]
    for entry in special_entries:
        bill[entry["type"]] = entry

    return render_template('detail.html', bill=bill)
