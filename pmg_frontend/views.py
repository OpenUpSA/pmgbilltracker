from flask import request, make_response, url_for, session, render_template, abort, send_from_directory, redirect
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
def index(year=date.today().year, bill_type=None):
    """
    Display a list of available bills, with some summary info and a link to each bill's detail page.
    """

    try:
        year = int(year)
    except ValueError as e:
        logger.debug(e)
        abort(400)

    current_year = date.today().year

    tmp = "bill"
    page_title = "All bills"
    year_list = range(current_year, 2005, -1)
    if bill_type and bill_type.lower() in ["pmb", "draft", "current"]:
        tmp = bill_type.lower()
        if bill_type.lower() == "pmb":
            page_title = "Private Member Bills"
            year_list = range(current_year, 2011, -1)
        elif bill_type.lower() == "draft":
            page_title = "Draft Bills"
            year_list = range(current_year, 2007, -1)
        elif bill_type.lower() == "current":
            page_title = "Current Bills"
            year = None
            year_list = []

    logger.debug("landing page called")
    if year:
        r = requests.get("http://" + API_HOST + "/" + tmp + "/year/" + str(year) + "/")
    else:
        r = requests.get("http://" + API_HOST + "/" + tmp + "/")
    bills = r.json()

    return render_template('index.html', title=page_title, bill_type=bill_type, year_list=year_list, year=year, bills=bills, api_host=API_HOST)


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


@app.route('/uploads/<path:file_name>')
def uploads(file_name):
    """
    Serve uploaded files from the Flask dev server. On staging or production, these should be served by Nginx.
    """

    logger.debug("uploads called")
    logger.debug(app.instance_path)
    logger.debug(file_name)
    return send_from_directory(app.config['UPLOAD_PATH'], file_name, as_attachment=True)