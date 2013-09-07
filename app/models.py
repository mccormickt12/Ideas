from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    major = db.Column(db.String(64))
    minor = db.Column(db.String(64))
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(64))
    year = db.Column(db.String(64))
    projects = db.relationship('Project', backref = 'author', lazy = 'dynamic')
    
    @property
    def short_url(self):
        return libraries.short_url.encode_url(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team = db.relationship('User', backref = 'project', lazy = 'dynamic')

    def __repr__(self):
        return '<Project %r>' % (self.name)
