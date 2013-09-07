from app import app
from flask import render_template
from app.models import User, Project
from wtforms import Form, BooleanField, TextField, PasswordField, validators

@app.route('/')
def index():
    return render_template('index.html', active="home")

@app.route('/example/')
def example():
    return render_template('example.html', active="example")

@app.route('/facebook/')
def facebook():
    return render_template('facebook.html', active="facebook")

@app.route('/example2/')
def example2():
    return render_template('example.html', active="example2", names=["Samir", "Shanti", "Tom"])

@app.route('/create/')
def create():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('create.html', active="create")

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])