from flask import request, make_response, url_for, session, render_template
from pmg_backend import app
import requests
import simplejson
from datetime import datetime, date
from logging import getLogger
from models import *
from pmg_backend import db, logger


class CustomEncoder(simplejson.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            try:
                encoded_obj = simplejson.dumps(obj.to_dict(), cls=CustomEncoder)
                logger.debug(encoded_obj)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = simplejson.JSONEncoder.default(self, obj)
        return encoded_obj


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
        out = bill_obj.to_dict()

    else:
        out = []
        bill_set = Bill.query.order_by(Bill.year.desc()).all()
        for bill_obj in bill_set:
            out.append(bill_obj.to_dict(include_related=False))

    response = make_response(simplejson.dumps(out, cls=CustomEncoder))
    response.mimetype = "application/json"
    return response
