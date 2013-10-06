from pmg_backend import app
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from models import *
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op

admin = Admin(app, name='PMG Bill Tracker')

# views for CRUD admin
admin.add_view(ModelView(Bill, db.session))
admin.add_view(ModelView(Event, db.session))

# manage static files from admin view
path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/uploads/', name='Uploaded Files'))

