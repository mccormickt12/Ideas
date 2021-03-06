from app import app, db
from flask import render_template, request, url_for, flash, redirect, session
from app.models import User, Project, YES, NO
from wtforms import Form, BooleanField, FileField, TextField, TextAreaField, PasswordField, validators, SelectField
from hashlib import md5
from werkzeug.routing import BaseConverter
from werkzeug import secure_filename
import os



class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter
MAX_UPLOAD_SIZE = 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get('logged_in'))


@app.route('/home/')
def home():
    user = User.query.filter_by(id=session.get('user_id'))
    if session.get('logged_in') and user.first():
        user = user[0]
        return render_template('home.html', user=user, logged_in=session.get('logged_in'))
    else:
        return redirect(url_for('login'))

@app.route('/home/edit', methods=['GET', 'POST'])
def edit_profile():
    user = User.query.filter_by(id=session.get('user_id'))
    if session.get('logged_in') and user.first():
        user = user[0]
        form = RegistrationForm()
        if request.method == 'POST' and form.validate():
            user.name=form.name.data
            user.user_name=form.user_name.data
            user.email=form.email.data
            user.major=form.major.data
            user.minor=form.minor.data
            user.year=form.year.data
            flash("Changes successfully made")
            return redirect(url_for('home'))
        else:
            form.name.data = user.name
            form.user_name.data=user.user_name
            form.email.data=user.email
            form.major.data=user.major
            form.minor.data=user.minor
            form.year.data=user.year

        return render_template('edit_profile.html', form=form, logged_in=session.get('logged_in'))
    else:
        return redirect(url('login'))

@app.route('/discover/')
def discover():
    projects = Project.query.all()
    projects = projects[::-1]
    users = User.query.all()
    return render_template('discover.html', projects=projects, User=User, logged_in=session.get('logged_in'))



@app.route('/create/', methods=['POST', 'GET'])
def create():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        un = User.query.filter_by(user_name=form.user_name.data)
        e = User.query.filter_by(email=form.email.data)
        if un.first() or e.first():
            flash("We already have that username or email.")
        elif " " in form.user_name.data:
            flash("No spaces allowed in your username")
        else:
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
        if request.files.get('image', None):
            
            file = request.files['image']
            if len(file.filename) == 0: 
                flash("Please upload a file.")
                return render_template('new_project.html', active="project", form=form, logged_in=session.get('logged_in')) 
            
            #Check whether file is the correct format (png, jpg, jpeg, or gif)
            if not allowed_file(file.filename):
                flash("Please upload a png, jpg, or gif type photo")
                return render_template('new_project.html', active="project", form=form, logged_in=session.get('logged_in')) 

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = filename.rsplit('.', 1)[1]


                #Temporarily write File to images folder
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))                    

                #Check File Size
                temp = open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                size = len(temp.read())
                if size > MAX_UPLOAD_SIZE:
                    flash("Please upload pictures less than 1mb.")
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return render_template('new_project.html', active="project", form=form, logged_in=session.get('logged_in')) 

                profile_url = os.path.join('static/img', filename)
                full_profile_url = 'app/' + profile_url
                
                # Save File to DB
                f = open(full_profile_url, 'rb')
                binary_contents = f.read()
                photo_file = binary_contents

                photo_exists = YES
                photo_name = filename
        else:
            flash("Please upload a file BITCH")
        
        project = Project(name=form.name.data, description=form.description.data, user_id=session.get('user_id'), photo_file=binary_contents, photo_exists=photo_exists, photo_name=photo_name)
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
            return redirect(url_for('home'))
        else:
            flash("Incorrect username and password")
    return render_template('login.html', form=form, logged_in=session.get('logged_in'))

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    session.clear()
    flash("You've been logged out")
    return redirect('/')


@app.route('/<regex("[A-Za-z0-9-_.]{4,20}"):uname>/')
def user_page(uname):
    user = db.session.query(User).filter_by(user_name = uname)
    if user.first():
        user = user[0]
        return render_template('user.html', user=user, logged_in=session.get('logged_in'), me=session.get('user_id'),
            projects=user.getFollowing())
    else:
        return render_template('error.html'), 404

@app.route('/<regex("[A-Za-z0-9-_.]{4,20}"):uname>/<regex("[ A-Za-z0-9-_.%]{4,20}"):proj>', methods=['GET', 'POST'])
def proj_page(uname, proj):
    user = db.session.query(User).filter_by(user_name = uname)
    if user.first():
        user = user[0]
        project = db.session.query(Project).filter_by(name = proj, user_id = user.id)
        if project.first():
            project = project[0]
            if request.method == 'POST':
                if request.form.get('join'):
                    if project.addFollower(session.get('user_id')):
                        flash("You have now joined this project")
                    else: 
                        flash("Already joined this project")
                elif request.form.get('remove'):
                    db.session.delete(project)
                    db.session.commit()
                    flash("Project successfully deleted")
                    return redirect(url_for('discover'))
            return render_template('project.html', user = user, project = project, logged_in=session.get('logged_in'),
             me=session.get('user_id'), num_followers=len(project.getFollowers()))
    return render_template('error.html')


@app.route('/<regex("[A-Za-z0-9-_.]{4,20}"):uname>/<regex("[ A-Za-z0-9-_.%]{4,20}"):proj>/edit/', methods=['GET', 'POST'])
def edit_proj(uname, proj):
    user = db.session.query(User).filter_by(user_name = uname)
    if user.first():
        user = user[0]
        project = db.session.query(Project).filter_by(name = proj, user_id = user.id)
        if project.first():
            project = project[0]
            if session.get('logged_in') and user.id == session.get('user_id'):
                form = ProjectForm(request.form)
                if request.method == 'POST':
                    if request.form.get('remove'):
                        db.session.delete(project)
                        db.session.commit()
                        flash("Project successfully deleted")
                        return redirect(url_for('user_page', uname=uname))
                    elif form.validate():
                        project.name = form.name.data
                        project.about = form.about.data
                        project.help = form.help.data
                        project.description = form.description.data
                        project.progress = form.description.data
                        db.session.commit()
                        return redirect(url_for('proj_page', uname=uname, proj=proj, logged_in=session.get('logged_in')))
                else:
                    form.name.data = project.name
                    form.about.data = project.about
                    form.help.data = project.help
                    form.description.data = project.description
                    form.progress.data = project.progress
                return render_template('edit.html', user=user, project=project, form=form, logged_in=session.get('logged_in'))
            else:
                return redirect(url_for('proj_page', uname=uname, proj=proj, logged_in=session.get('logged_in')))
    return render_template('error.html')


@app.route('/<regex("[A-Za-z0-9-_.]{4,20}"):uname>/<regex("[ A-Za-z0-9-_.%]{4,20}"):proj>/apply/', methods=['GET', 'POST'])
def apply(uname, proj):
    if session.get('logged_in'):
        form = ApplyForm()
        me = User.query.filter_by(id=session.get('user_id'))
        user = User.query.filter_by(user_name = uname)
        if me.first() and user.first():
            me = me[0]
            user = user[0]
            project = Project.query.filter_by(name = proj, user_id = user.id)
            if project.first():
                project = project[0]
            else:
                return redirect(url_for('proj_page', uname=uname, proj=proj))
        else:
            return redirect(url_for('proj_page', uname=uname, proj=proj))
        if request.method == 'POST' and form.validate():
            flash('form validated')
            req = Request(requestor_id=me.id, user_id=user.id, proj_id=project.id, username=user.user_name,
            skills = form.skills.data, reason = form.why.data)
            db.session.add(req)
            db.session.commit()
            flash("Request to join project sucecessful")
            return redirect(url_for('proj_page', proj=proj, uname=uname))
        elif user.id == me.id:
            flash("Cannot apply to your own project")
            return redirect(url_for('proj_page', proj=proj, uname=uname))
        else:
            form.username.data = me.user_name
        return render_template('apply.html', form=form, logged_in=session.get('logged_in'), 
            user=user, me=me)
    else:
        return redirect(url_for('login'))


@app.route('/<regex(".+"):url>')
def error():
    return render_template('error.html')

class RegistrationForm(Form):
    name = TextField('Name', [validators.Length(min=4, max=25)])
    user_name = TextField('User name', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    major = TextField('Major', [validators.Length(min=2, max=30)])
    minor = TextField('Minor')
    year = SelectField('Year', choices=[("Freshman", "Freshman"), ("Sophomore", "Sophomore"),
     ("Junior", "Junior"), ("Senior", "Senior"), ("Super Senior", "Super Senior"),
     ("Grad Student", "Grad Student"), ("Alumni", "Alumni")])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])


class ProjectForm(Form):
    name = TextField('Name', [validators.Length(min=2, max=25)])
    about = TextAreaField('About the Team', [validators.Length(min=10, max=400)])
    help = TextAreaField('How can people help', [validators.Length(min=10, max=400)])
    description = TextAreaField('Project Description', [validators.Length(min=10, max=400)])
    progress = SelectField('Progress', choices=[("Plan", "Plan"), ("Started", "Started"),
     ("Ongoing", "Ongoing"), ("Completed", "Completed")])
    image = FileField('Project Image')


class ApplyForm(Form):
    username = TextField('Username', [validators.Length(min=2, max=25)])
    skills = TextAreaField("What skills do you offer? ", [validators.Length(min=2, max=400)])
    why = TextAreaField("Why do you want to help? ", [validators.Length(min=2, max=400)])

class LoginForm(Form):
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

def auth_user(user_id):
    session['user_id'] = user_id
    session['logged_in'] = True

def allowed_file(filename):
    return '.' in filename and \
           (filename.rsplit('.', 1)[1]).lower() in ALLOWED_EXTENSIONS



