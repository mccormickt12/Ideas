from app import app, db
from flask import render_template, request, url_for, flash, redirect, session
from app.models import User, Project
from wtforms import Form, BooleanField, TextField, TextAreaField, PasswordField, validators
from hashlib import md5
from werkzeug.routing import BaseConverter



class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get('logged_in'))

@app.route('/discover/')
def discover():
    projects = Project.query.all()
    users = User.query.all()
    return render_template('discover.html', projects=projects, User=User, logged_in=session.get('logged_in'))



@app.route('/create/', methods=['POST', 'GET'])
def create():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data, user_name=form.user_name.data, 
                    email=form.email.data, password=md5(form.password.data).hexdigest(),
                    major=form.major.data, minor=form.minor.data,
                    year=form.year.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('discover'))
    return render_template('create.html', active="create", form=form, logged_in=session.get('logged_in'))


@app.route('/new/project', methods=['POST', 'GET'])
def start():
    if session.get('logged_in'):
        logged_in = True
    else:
        logged_in = False
        flash("You must login first to do this")
        return redirect(url_for('login'))
    form = ProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        if ' ' in form.name.data:
            flash("Project cannot have spaces, try underscores or dashes instead!")
            return render_template('new_project.html', active="project", form=form, logged_in=session.get('logged_in')) 
        project = Project(name=form.name.data, description=form.description.data, user_id=session.get('user_id'))
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('discover'))
    return render_template('new_project.html', active="project", form=form, logged_in=session.get('logged_in'))

@app.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)

    if session.get('logged_in'):
        logged_in = True
    else:
        logged_in = False

    if request.method=='POST' and form.validate():
        
        #Returns a list of users, should be one.
        user = db.session.query(User).filter_by(email = form.email.data, password = md5(form.password.data).hexdigest() )
        
        # If user exists
        if user.first():
            user = user[0]
            flash(u'Successfully logged in as %s' % user.name)
            auth_user(user.id)
            return redirect(url_for('login'))
        else:
            flash("Incorrect username and password")
    return render_template('login.html', form=form, logged_in=session.get('logged_in'))

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    session.clear()
    flash("You've been logged out")
    return redirect('/')


@app.route('/<regex("[A-Za-z0-9]{4,20}"):uname>/')
def user_page(uname):
    user = db.session.query(User).filter_by(user_name = uname)
    if user.first():
        user = user[0]
        return render_template('user.html', user=user, logged_in=session.get('logged_in'), me=session.get('user_id'))
    else:
        return render_template('error.html'), 404

@app.route('/<regex("[A-Za-z0-9]{4,20}"):uname>/<regex("[ A-Za-z0-9-_%]{4,20}"):proj>', methods=['GET', 'POST'])
def proj_page(uname, proj):
    user = db.session.query(User).filter_by(user_name = uname)
    if user.first():
        user = user[0]
        project = db.session.query(Project).filter_by(name = proj, user_id = user.id)
        if project.first():
            project = project[0]
            if request.method == 'POST':
                if project.addMember(user.id):
                    flash("You have now joined this project")
                else: 
                    flash("Already joined this project")
            return render_template('project.html', user = user, project = project, logged_in=session.get('logged_in'), me=session.get('user_id'))
    return render_template('error.html')


@app.route('/<regex("[A-Za-z0-9]{4,20}"):uname>/<regex("[ A-Za-z0-9-_%]{4,20}"):proj>/edit/', methods=['GET', 'POST'])
def edit_proj(uname, proj):
    
    user = db.session.query(User).filter_by(user_name = uname)
    if user.first():
        user = user[0]
        project = db.session.query(Project).filter_by(name = proj, user_id = user.id)
        if project.first():
            project = project[0]
            if session.get('logged_in') and user.id == session.get('user_id'):
                form = ProjectForm(request.form)
                if request.method == 'POST' and form.validate():
                    project.name = form.name.data
                    project.description = form.description.data
                    db.session.commit()
                    return redirect(url_for('proj_page', uname=uname, proj=proj, logged_in=session.get('logged_in')))
                else:
                    form.name.data = project.name
                    form.description.data = project.description
                return render_template('edit.html', user=user, project=project, form=form, logged_in=session.get('logged_in'))
            else:
                return redirect(url_for('proj_page', uname=uname, proj=proj, logged_in=session.get('logged_in')))
    return render_template('error.html')





class RegistrationForm(Form):
    name = TextField('Name', [validators.Length(min=4, max=25)])
    user_name = TextField('User name', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    major = TextField('Major', [validators.Length(min=2, max=30)])
    minor = TextField('Minor', [validators.Length(min=2, max=30)])
    year = TextField('Year', [validators.Length(min=2, max=30)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])


class ProjectForm(Form):
    name = TextField('Name', [validators.Length(min=4, max=25)])
    description = TextAreaField('Description', [validators.Length(min=10, max=400)])

class LoginForm(Form):
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

def auth_user(user_id):
    session['user_id'] = user_id
    session['logged_in'] = True




