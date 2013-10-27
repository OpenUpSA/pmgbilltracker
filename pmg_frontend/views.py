from flask import request, make_response, url_for, session, render_template
from pmg_frontend import app
import requests
import simplejson
from datetime import datetime, date
from pmg_frontend import logger


@app.route('/')
def landing():
    """

    """

    logger.debug("landing page called")

    return render_template('index.html')