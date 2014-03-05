from pmg_backend import app
from flask.ext.admin import Admin, form, BaseView, AdminIndexView, expose
from flask.ext.admin.contrib.sqla import ModelView
from models import Bill, Entry, Agent, db
from flask.ext.admin.contrib.fileadmin import FileAdmin
from wtforms.fields import SelectField, TextAreaField
import datetime


class BillView(ModelView):
    can_create = False
    can_delete = False
    column_list = ('name', 'code', 'bill_type', 'status')
    column_searchable_list = ('code', 'name')
    page_size = 50
    form_excluded_columns = ('entries', )
    form_overrides = dict(bill_type=SelectField, status=SelectField, objective=TextAreaField)
    form_args = {
        # Pass the choices to the `SelectField`
        "bill_type" : {
            "choices" : [
                ("Section 75 (Ordinary Bills not affecting the provinces)", "Section 75 (Ordinary Bills not affecting the provinces)"),
                ("Section 76 (Ordinary Bills affecting the provinces)", "Section 76 (Ordinary Bills affecting the provinces)"),
                ("Other", "Other"),
            ]
        },
        "status" : {
            "choices":[
                (None, "Unknown"),
                ("na", "In progress - NA"),
                ("ncop", "In progress - NCOP"),
                ("assent", "Sent to the President"),
                ("enacted", "Enacted"),
                ("withdrawn", "Withdrawn")
            ]
        }
    }

entry_types = [
    "other",
    "gazette", "memorandum", "greenpaper",
    "whitepaper", "draft", "bill",
    "pmg-meeting-report", "public-hearing",
    "committee-report", "hansard-minutes",
    "vote-count",
]

entry_type_choices = []
for entry_type in entry_types:
    entry_type_choices.append((entry_type, entry_type))


class EntryView(ModelView):
    form_overrides = dict(type=SelectField, location=SelectField, notes=TextAreaField)
    form_args = {
        # Pass the choices to the `SelectField`
        "type":{
            "choices": entry_type_choices
        },
        "location":{
            "choices": [
                ("null", "Unknown"),
                ("1", "National Assembly (NA)"),
                ("2", "National Council of Provinces (NCOP)"),
                ("3", "President's Office"),
            ]
        },
    }


class HomeView(AdminIndexView):
    @expose("/")
    def index(self):

        return self.render('admin/home.html')


admin = Admin(app, name='PMG Bill Tracker', base_template='admin/my_master.html', index_view=HomeView(name='Home'))

admin.add_view(BillView(Bill, db.session, name="Bills"))
admin.add_view(EntryView(Entry, db.session, name="Entries"))

# views for CRUD admin
admin.add_view(ModelView(Agent, db.session, name="Agents"))
