from flask import request, make_response, url_for, session, render_template
from pmg_backend import app
from models import *
from pmg_backend import db, logger
from serializers import BaseSerializer

base_serializer = BaseSerializer()


@app.route('/')
def autodiscover():
    """
    Provide a landing page that documents the API endpoints that are available, and provides a link
    to the admin interface.
    """

    logger.debug("landing page called")

    return render_template('index.html')


@app.route('/bill/')
@app.route('/bill/<bill_id>/')
def bill(bill_id=None):

    logger.debug("Bill endpoint called")
    if bill_id:
        bill_obj = Bill.query.get_or_404(bill_id)
        out = base_serializer.serialize(bill_obj)

    else:
        bill_set = Bill.query.order_by(Bill.year.desc()).all()
        out = base_serializer.serialize(bill_set)

    response = make_response(out)
    response.mimetype = "application/json"
    return response
