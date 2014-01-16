from flask import request, make_response, url_for, session, render_template, abort, redirect
from pmg_frontend import app
import requests
import simplejson
from datetime import datetime, date
from pmg_frontend import logger


API_HOST = app.config['API_HOST']

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

    try:
        if year is not None:
            year = int(year)
    except ValueError as e:
        logger.debug(e)
        abort(400)

    start_year = date.today().year

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
                year_list = []
        logger.debug("landing page called")
        status_dict = {
            "na": ("in progress", "label-primary"),
            "ncop": ("in progress", "label-primary"),
            "assent": ("sent to the president", "label-warning"),
            "enacted": ("signed into law", "label-success"),
            "withdrawn": ("withdrawn", "label-default"),
            }

        api_url = "http://" + API_HOST + "/" + tmp + "/"

        if start_year:
            r = requests.get("http://" + API_HOST + "/" + tmp + "/year/" + str(start_year) + "/")
        else:
            r = requests.get(api_url)
        bills = r.json()
        if not bills:
            start_year -= 1

    return render_template('index.html', title=page_title, bill_type=bill_type, year_list=year_list,
                           year=start_year, bills=bills, status_dict=status_dict, api_url=api_url)


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
        abort(400)

    logger.debug("detail page called")
    r = requests.get("http://" + API_HOST + "/bill/" + str(bill_id) + "/")
    bill = r.json()

    return render_template('detail.html', bill=bill)