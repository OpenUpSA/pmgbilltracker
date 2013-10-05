from fabric.api import *


def setup():
    sudo('pip install Flask')
    sudo('pip install Flask-SQLAlchemy')
    sudo('pip install Flask-Admin')
    sudo('pip install Flask-WTF==0.8.4')  # version 0.9.3 breaks support for flask-admin's file admin