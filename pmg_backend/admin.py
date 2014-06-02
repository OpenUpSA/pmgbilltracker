from pmg_backend import app
from flask.ext.admin import Admin, AdminIndexView, expose, helpers
from flask.ext.admin.contrib.sqla import ModelView
from models import User, Bill, Entry, Agent, db
from flask.ext.admin.model.template import macro
from wtforms.fields import SelectField, TextAreaField
from flask.ext.admin.form import rules
from wtforms import form, fields, validators
from flask import request, url_for, redirect, flash
from flask.ext import login
from sqlalchemy import func

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
    email = fields.TextField(validators=[validators.required(), validators.email()])
    password = fields.PasswordField(
        validators=[
            validators.required(),
            validators.length(min=6, message="Your password needs to have at least six characters.")
        ]
    )

    def validate_login(self, field):
        if db.session.query(User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate users')


class MyModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50
    column_exclude_list = ['is_deleted', ]

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def get_query(self):
        """
        Add filter to return only non-deleted records.
        """
        return self.session.query(self.model).filter(self.model.is_deleted==False)

    def get_count_query(self):
        """
        Add filter to count only non-deleted records.
        """
        return self.session.query(func.count('*')).select_from(self.model).filter(self.model.is_deleted==False)

    def delete_model(self, model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            model.delete()
            self.session.add(model)
            self.session.commit()
            return True
        except Exception as ex:
            if self._debug:
                raise
            flash('Failed to delete model. %(error)s' % str(ex), 'error')
            self.session.rollback()
            return False


class BillView(MyModelView):
    can_create = False
    list_template = 'admin/custom_list_template.html'
    form_edit_rules = (
        'name',
        'code',
        'bill_type',
        'objective',
        'status',
        'entries'
    )
    column_list = ('name', 'code', 'bill_type', 'status', 'entries', 'related_docs')
    column_searchable_list = ('code', 'name')
    column_formatters = dict(
        entries=macro('render_entries'),
        related_docs=macro('render_related_docs'),
        code=macro('render_code'),
        )
    form_overrides = dict(bill_type=SelectField, status=SelectField, objective=TextAreaField)
    form_widget_args = {
        'code':{
            'disabled': True
        },
        'name': {
            'class': 'input-xxlarge'
        },
        'objective': {
            'class': 'input-xxlarge'
        }
    }
    form_args = {
        # Pass the choices to the `SelectField`
        "bill_type" : {
            "choices" : [
                ("Draft", "Draft Bill"),
                ("S74", "Section 74 (Constitutional amendments)"),
                ("S75", "Section 75 (Ordinary Bills not affecting the provinces)"),
                ("S76", "Section 76 (Ordinary Bills affecting the provinces)"),
                ("S77", "Section 77 (Money Bills)"),
                ("", "Unknown"),
                ]
        },
        "status" : {
            "choices":[
                ("", "Unknown"),
                ("na", "In progress - NA"),
                ("ncop", "In progress - NCOP"),
                ("returned-to-na", "Returned with amendments - NA"),
                ("president", "Sent to the President"),
                ("enacted", "Enacted"),
                ("withdrawn", "Withdrawn"),
                ("lapsed", "Lapsed"),
                ]
        }
    }

    def update_model(self, form, model):

        del form.code
        return super(MyModelView, self).update_model(form=form, model=model)

entry_types = [
    "default",
    "committee-meeting", "public-hearing",
    "committee-report", "hansard",
    "vote-count",
    ]

related_doc_types = [
    "gazette", "memorandum", "greenpaper",
    "whitepaper", "draft", "bill-version", "act", "original-act",
    ]

entry_type_choices = []
for entry_type in entry_types:
    entry_type_choices.append((entry_type, entry_type))

related_doc_choices = []
for related_doc_type in related_doc_types:
    related_doc_choices.append((related_doc_type, related_doc_type))


class EntryView(MyModelView):
    list_template = 'admin/custom_list_template.html'
    form_create_rules = (
        'date',
        'bills',
        'location',
        'agent',
        'type',
        'title',
        'description',
        'url')
    form_edit_rules = form_create_rules
    column_list = (
        'date',
        'bills',
        'type',
        'agent',
        'url',
        'title',
        'description',
        'location')
    column_formatters = dict(
        location=macro('render_location'),
        date=macro('render_date'),
        url=macro('render_url'),
        bills=macro('render_bills'),
        )
    form_overrides = dict(type=SelectField, location=SelectField, description=TextAreaField)
    form_args = {
        # Pass the choices to the `SelectField`
        "type":{
            "choices": entry_type_choices
        },
        "location":{
            "choices": [
                ("", "Unknown"),
                ("1", "National Assembly (NA)"),
                ("2", "National Council of Provinces (NCOP)"),
                ("3", "President's Office"),
                ("4", "Joint consideration (NA+NCOP)"),
                ]
        },
    }
    form_widget_args = {
        'title': {
            'class': 'input-xxlarge'
        },
        'description': {
            'class': 'input-xxlarge'
        },
        'url': {
            'class': 'input-xxlarge'
        }
    }

    def get_query(self):
        """
        Add filter to return only non-deleted records.
        """
        query = self.session.query(self.model) \
            .filter(self.model.is_deleted==False) \
            .filter(Entry.type.in_(entry_types))
        if request.args.get('bill_id'):
            try:
                bill = Bill.query.get(request.args['bill_id'])
                self._template_args['filtered_bill'] = bill
                query = query.filter(Entry.bills.any(bill_id=request.args['bill_id']))
            except Exception, e:
                pass
        return query

    def get_count_query(self):
        """
        Add filter to count only non-deleted records.
        """
        query = self.session.query(func.count('*')).select_from(Entry) \
            .filter(Entry.is_deleted==False) \
            .filter(Entry.type.in_(entry_types))
        if request.args.get('bill_id'):
            query = query.filter(Entry.bills.any(bill_id=request.args['bill_id']))
        return query


class RelatedDocView(MyModelView):
    list_template = 'admin/custom_list_template.html'
    form_create_rules = ('type', 'bills', 'title', 'url')
    form_edit_rules = form_create_rules
    column_list = ('type', 'bills', 'title', 'url')
    column_formatters = dict(
        url=macro('render_url'),
        bills=macro('render_bills'),
        )
    form_overrides = dict(type=SelectField,)
    form_args = {
        # Pass the choices to the `SelectField`
        "type":{
            "choices": related_doc_choices
        },
    }
    form_widget_args = {
        'title': {
            'class': 'input-xxlarge'
        },
        'url': {
            'class': 'input-xxlarge'
        }
    }

    def get_query(self):
        """
        Add filter to return only non-deleted records.
        """
        query = self.session.query(self.model) \
            .filter(self.model.is_deleted==False) \
            .filter(Entry.type.in_(related_doc_types))
        if request.args.get('bill_id'):
            try:
                bill = Bill.query.get(request.args['bill_id'])
                self._template_args['filtered_bill'] = bill
                query = query.filter(Entry.bills.any(bill_id=request.args['bill_id']))
            except Exception, e:
                pass
        return query

    def get_count_query(self):
        """
        Add filter to count only non-deleted records.
        """
        query = self.session.query(func.count('*')).select_from(Entry) \
            .filter(Entry.is_deleted==False) \
            .filter(Entry.type.in_(related_doc_types))
        if request.args.get('bill_id'):
            query = query.filter(Entry.bills.any(bill_id=request.args['bill_id']))
        return query


class AgentView(MyModelView):
    list_template = 'admin/custom_list_template.html'
    column_searchable_list = ('name', )
    form_create_rules = (
        'name',
        'type',
        'url',
        'location',
    )
    form_edit_rules = form_create_rules
    column_formatters = dict(
        location=macro('render_location'),
        url=macro('render_url'),
        )
    form_overrides = dict(location=SelectField, type=SelectField)
    form_args = {
        # Pass the choices to the `SelectField`
        "location":{
            "choices": [
                ("", "Unknown"),
                ("1", "National Assembly (NA)"),
                ("2", "National Council of Provinces (NCOP)"),
                ("3", "President's Office"),
                ("4", "Joint consideration (NA+NCOP)"),
                ]
        },
        "type":{
            "choices": [
                ("committee", "Committee"),
                ("minister", "Minister"),
                ("president", "The President"),
                ("house", "House of Parliament"),
                ]
        },
    }
    form_widget_args = {
        'name': {
            'class': 'input-xxlarge'
        },
        'url': {
            'class': 'input-xxlarge'
        }
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
            if user:
                if not user.is_active():
                    flash('Your account has not been activated. Please contact the site administrator.' , 'error')
                    return redirect(url_for('.login_view'))
                else:
                    login.login_user(user)
            else:
                flash('Username or Password is invalid' , 'error')
                return redirect(url_for('.login_view'))

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        return self.render('admin/home.html', form=form, link=link)

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            # hash password, before populating User object
            form.password.data = hash(form.password.data)
            form.populate_obj(user)

            # activate the admin user
            if user.email == app.config['ADMIN_USER']:
                user.is_active = True

            db.session.add(user)
            db.session.commit()

            flash('Please wait for your new account to be activated.', 'info')
            return redirect(url_for('.login_view'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        return self.render('admin/home.html', form=form, link=link, register=True)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = ".login_view"

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

init_login()

admin = Admin(app, name='PMG Bill Tracker', base_template='admin/my_master.html', index_view=HomeView(name='Home'))

admin.add_view(BillView(Bill, db.session, name="Bills", endpoint='bill'))
admin.add_view(EntryView(Entry, db.session, name="Entries", endpoint='entry'))
admin.add_view(RelatedDocView(Entry, db.session, name="Related documents", endpoint='related-docs'))
admin.add_view(AgentView(Agent, db.session, name="Agents", endpoint='agent'))
