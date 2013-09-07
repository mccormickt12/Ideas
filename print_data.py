from app import models, db
from app.models import User, Project

def print_all_users():
    users = User.query.all()
    for u in users:
        if u:
            print u.id, u.name, u.major, u.email, u.password, u.year, 'essay: ' + str(u.essay), 'activated: ' + str(u.activated) + 'classes: ' + str(u.classes.all()) + ' intro: ' + str(u.introduction) + ' profile_exists: ' + str(u.photo_exists) + ' pick one: ' + str(u.choose_one)


def print_all_projects():
    projects = Project.query.all()
    for u in users:
        if u:
            print u.id, u.name, u.email

def remove_samir():
    results = db.session.query(models.User).filter_by(email="makhani@berkeley.edu").all()
    if len(results) > 0:
        samir = results[0]
        db.session.delete(samir)
        samir_classes = db.session.query(models.Classes).filter_by(user_id=samir.id).all()
        for one_class in samir_classes:
            db.session.delete(one_class)
        db.session.commit()
        print "samir has been deleted"


print "==================USERS=================="
print_all_users()
print "=================Projects================="
print_all_classes()
print "===============EXPERIENCES==============="
print_all_experiences()
