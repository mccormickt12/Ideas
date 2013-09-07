from app import app, db
from flask import render_template, request, url_for, flash, redirect
from app.models import User, Project
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from hashlib import md5

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

@app.route('/create/', methods=['POST', 'GET'])
def create():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data, email=form.email.data,
                    password=md5(form.password.data).hexdigest())
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('create'))
    return render_template('create.html', active="create", form=form)

class RegistrationForm(Form):
    name = TextField('Name', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])