from pmg_backend import app
from flask.ext.admin import Admin, AdminIndexView, expose, helpers
from flask.ext.admin.contrib.sqla import ModelView
from models import User, Bill, Entry, Agent, db
from flask.ext.admin.model.template import macro
from wtforms.fields import SelectField, TextAreaField
from flask.ext.admin.form import rules
from wtforms import form, fields, validators
from flask import request, url_for, redirect
from flask.ext import login

# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    email = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != hash(self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()


class RegistrationForm(form.Form):
    email = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate users')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


class MyModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = False
    page_size = 50

    def is_accessible(self):
        return login.current_user.is_authenticated()


class BillView(MyModelView):
    can_create = False
    list_template = 'admin/custom_list_template.html'
    column_list = ('name', 'code', 'bill_type', 'status', 'entries')
    column_searchable_list = ('code', 'name')
    column_formatters = dict(
        entries=macro('render_entries'),
        code=macro('render_code'),
        )
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
    "default",
    "gazette", "memorandum", "greenpaper",
    "whitepaper", "draft", "bill-version", "act",
    "pmg-meeting-report", "public-hearing",
    "committee-report", "hansard-minutes",
    "vote-count",
    ]

entry_type_choices = []
for entry_type in entry_types:
    entry_type_choices.append((entry_type, entry_type))


class EntryView(MyModelView):
    list_template = 'admin/custom_list_template.html'
    form_create_rules = (
        'date',
        'location',
        'agent',
        'type',
        'title',
        'description',
        'url')
    form_edit_rules = form_create_rules
    column_formatters = dict(
        location=macro('render_location'),
        date=macro('render_date'),
        url=macro('render_url'),
        )
    form_overrides = dict(type=SelectField, location=SelectField, description=TextAreaField)
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


class AgentView(MyModelView):
    list_template = 'admin/custom_list_template.html'
    column_formatters = dict(
        location=macro('render_location'),
        )
    form_overrides = dict(location=SelectField, )
    form_args = {
        # Pass the choices to the `SelectField`
        "location":{
            "choices": [
                ("null", "Unknown"),
                ("1", "National Assembly (NA)"),
                ("2", "National Council of Provinces (NCOP)"),
                ("3", "President's Office"),
                ]
        },
        }


# Customized index view that handles login & registration
class HomeView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return self.render('admin/home.html')

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return self.render('admin/home.html')

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            # hash password, before populating User object
            form.password.data = hash(form.password.data)
            form.populate_obj(user)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return self.render('admin/home.html')

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Initialize flask-login
init_login()

admin = Admin(app, name='PMG Bill Tracker', base_template='admin/my_master.html', index_view=HomeView(name='Home'))

admin.add_view(BillView(Bill, db.session, name="Bills", endpoint='bill'))
admin.add_view(EntryView(Entry, db.session, name="Entries", endpoint='entry'))
admin.add_view(AgentView(Agent, db.session, name="Agents", endpoint='agent'))
