from flask import request, make_response, url_for, session, render_template
from pmg_backend import app
from models import *
from pmg_backend import db, logger
from serializers import BillSerializer

bill_serializer = BillSerializer()

def make_json_response(bills, include_related=False):
    response = make_response(bill_serializer.serialize(bills, include_related=True))
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
    bills = Bill.query\
        .filter(Bill.bill_type=="B")\
        .filter(Bill.code.isnot(None))\
        .order_by(Bill.year.desc(), Bill.number.desc())\
        .all()

    if year:
        bills = bills.filter(Bill.year==int(year))
    return make_json_response(bills)


@app.route('/pmb/')
@app.route('/pmb/year/<year>/')
def pmb_list(year=None):

    pmb = Bill.query\
        .filter(Bill.bill_type=="PMB")\
        .order_by(Bill.number.desc())\
        .all()

    logger.debug("PMB list endpoint called")
    if year:
        pmb = pmb.filter(Bill.year==int(year))
    return make_json_response(pmb)

@app.route('/draft/')
@app.route('/draft/year/<year>/')
def draft_list(year=None):

    logger.debug("Draft list endpoint called")
    bills = Bill.query\
        .filter(Bill.code==None)\
        .order_by(Bill.number.desc())\
        .all()

    # TODO: set "draft" as a special bill_type
    if year:
        bills = bills.filter(Bill.year==int(year))
        return make_json_response(bilss, include_related=True)
    else:
        return make_json_response(bills)


@app.route('/current/')
def current_list(year=None):

    logger.debug("Current list endpoint called")
    tmp = Bill.query.filter(Bill.status != "enacted").filter(Bill.status != "withdrawn").filter(Bill.status != "expired").filter(Bill.status != None).order_by(Bill.year.desc(), Bill.number.desc()).all()
    response = make_response(bill_serializer.serialize(tmp))
    response.mimetype = "application/json"
    response.headers.add('Access-Control-Allow-Origin', "*")  # allow for ajax requests from frontend
    return response


@app.route('/bill/<bill_id>/')
def bill_detail(bill_id):

    logger.debug("Bill detail endpoint called")

    tmp = Bill.query.get_or_404(bill_id)
    response = make_response(bill_serializer.serialize(tmp, include_related=True))
    response.mimetype = "application/json"
    return response
