from pmg_backend import app
from flask.ext.admin import Admin, form, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from models import *
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op
from wtforms.fields import SelectField, TextAreaField

# base path for uploaded content
path = op.join(op.dirname(__file__), 'uploads')


class MyModelView(ModelView):
    create_template = 'admin/model/my_create.html'

    def __init__(self, model, session, **kwargs):
        super(MyModelView, self).__init__(model, session, **kwargs)


class BillView(ModelView):
    form_overrides = dict(bill_type=SelectField, objective=TextAreaField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        bill_type=dict(
            choices=[
                ("Section 75 (Ordinary Bills not affecting the provinces)", "Section 75 (Ordinary Bills not affecting the provinces)"),
                ("Section 76 (Ordinary Bills affecting the provinces)", "Section 76 (Ordinary Bills affecting the provinces)"),
                ("Other", "Other"),
                ]
        ))


class EventView(ModelView):
    #column_list = ('bill', 'stage', 'content')
    inline_models = [
        (
            Content,
            dict(
                form_overrides={
                    'url': form.FileUploadField
                },
                form_args={
                    'url': {
                        'label': 'File',
                        'base_path': path
                    }
                }
            )
        )
    ]

admin = Admin(app, name='PMG Bill Tracker', base_template='admin/my_master.html')

admin.add_view(BillView(Bill, db.session))
admin.add_view(EventView(Event, db.session))

# views for CRUD admin
admin.add_view(ModelView(Agent, db.session))
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Stage, db.session))

# manage static files from admin view
admin.add_view(FileAdmin(path, '/uploads/', name='Uploaded Files'))