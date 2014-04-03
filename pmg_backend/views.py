from flask import request, make_response, url_for, session, render_template, abort
from pmg_backend import app
from models import Bill
from pmg_backend import db, logger
from serializers import BillSerializer

bill_serializer = BillSerializer()
error_bad_request = 400

def make_json_response(bills, include_related=False):
    response = make_response(bill_serializer.serialize(bills, include_related))
    response.mimetype = "application/json"
    response.headers.add('Access-Control-Allow-Origin', "*")  # allow for ajax requests from frontend
    return response

@app.route('/')
def autodiscover():
    """
    Provide a landing page that documents the API endpoints that are available, and provides a link
    to the admin interface.
    """

    logger.debug("landing page called")

    return render_template('index.html')

@app.route('/bill/')
@app.route('/bill/year/<year>/')
def bill_list(year=None):

    logger.debug("Bill list endpoint called")
    bills = Bill.regular_bills\
        .filter(Bill.code.isnot(None))\
        .order_by(Bill.year.desc(), Bill.number.desc())

    if year:
        bills = bills.filter(Bill.year==int(year))
    return make_json_response(bills)


@app.route('/pmb/')
@app.route('/pmb/year/<year>/')
def pmb_list(year=None):

    pmb = Bill.pmb.order_by(Bill.number.desc())

    logger.debug("PMB list endpoint called")
    if year:
        pmb = pmb.filter(Bill.year==int(year))
    return make_json_response(pmb)

@app.route('/draft/')
@app.route('/draft/year/<year>/')
def draft_list(year=None):

    logger.debug("Draft list endpoint called")
    bills = Bill.draft_bills.order_by(Bill.number.desc())

    if year:
        bills = bills.filter(Bill.year==int(year))
        return make_json_response(bills, include_related=True)
    else:
        return make_json_response(bills)

@app.route('/current/')
def current_list(year=None):

    logger.debug("Current list endpoint called")
    
    bills = Bill.current_bills\
        .order_by(Bill.year.desc(), Bill.number.desc())

    return make_json_response(bills)


@app.route('/bill/<bill_id>/')
def bill_detail(bill_id):

    logger.debug("Bill detail endpoint called")

    bill = Bill.query.get_or_404(bill_id)
    return make_json_response(bill, include_related=True)


@app.route('/bill/<bill_prefix>-<bill_year>/')
def bill_detail_from_code(bill_prefix, bill_year):

    logger.debug("Bill detail-from-code endpoint called")

    try:
        bill_year = int(bill_year)
        bill_code = bill_prefix + "-" + str(bill_year)
    except:
        abort(error_bad_request)

    bill = Bill.query.filter(Bill.code==bill_code).first()
    return make_json_response(bill, include_related=True)
