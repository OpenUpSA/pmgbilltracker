from pmg_backend import app
from flask.ext.admin import Admin, form, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from models import *
from flask.ext.admin.contrib.fileadmin import FileAdmin
from wtforms.fields import SelectField, TextAreaField

# base path for uploaded content
upload_path = app.config['UPLOAD_PATH']


class BillView(ModelView):
    form_excluded_columns = ('content', )
    form_overrides = dict(bill_type=SelectField, status=SelectField, objective=TextAreaField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        bill_type=dict(
            choices=[
                ("Section 75 (Ordinary Bills not affecting the provinces)", "Section 75 (Ordinary Bills not affecting the provinces)"),
                ("Section 76 (Ordinary Bills affecting the provinces)", "Section 76 (Ordinary Bills affecting the provinces)"),
                ("Other", "Other"),
            ]
        ),
        status=dict(
            choices=[
                (None, "Unknown status"),
                ("100", "Accepted by NA only"),
                ("110", "Accepted by NA & NCOP"),
                ("010", "Accepted by NCOP only"),
                ("010", "Amended by NCOP, needs NA approval"),
                ("100", "Amended by NA, needs NCOP approval"),
                ("111", "Signed into Law"),
                ("Waiting to be introduced", "Waiting to be introduced"),
                ("Withdrawn", "Withdrawn"),
            ]
        )
    )

entry_types = [
        "gazette",
        "memorandum",
        "greenpaper",
        "whitepaper",
        "draft",
        "bill",
        "pmg-meeting-report",
        "committee-report",
        "hansard-minutes",
        "vote-count",
        "other",
        ]

entry_type_choices = []
for entry_type in entry_types:
    entry_type_choices.append((entry_type, entry_type))


class EntryView(ModelView):
    form_overrides = dict(type=SelectField, location=SelectField, stage=SelectField, notes=TextAreaField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        type=dict(
            choices=entry_type_choices
        ),
        location=dict(
            choices=[
                (None, "Unknown"),
                (1, "National Assembly (NA)"),
                (2, "National Council of Provinces (NCOP)"),
                (3, "President's Office"),
            ]
        ),
        stage=dict(
            choices=[
                (None, "Unknown"),
                (1, "Introduced"),
                (2, "Before committee"),
                (3, "Awaiting approval"),
                (4, "Mediation"),
            ]
        )
    )
    # TODO: add inline file upload / select existing uploads / paste raw url

admin = Admin(app, name='PMG Bill Tracker', base_template='admin/my_master.html')

admin.add_view(FileAdmin(upload_path, '/uploads/', name='Uploads'))

admin.add_view(BillView(Bill, db.session, name="Bills"))
admin.add_view(EntryView(Entry, db.session, name="Entries"))

# views for CRUD admin
admin.add_view(ModelView(Agent, db.session, name="Agents"))

#admin.add_view(ModelView(Tag, db.session, name="Tags"))
