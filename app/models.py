from app import db

YES = 1
NO = 0


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    user_name = db.Column(db.String(64))
    major = db.Column(db.String(64))
    minor = db.Column(db.String(64))
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(64))
    year = db.Column(db.String(64))
    photo_exists = db.Column(db.SmallInteger, default = NO)
    photo_file = db.Column(db.LargeBinary(1000000))
    photo_name = db.Column(db.String(64))
    progress = db.Column(db.String(64))
    activated = db.Column(db.SmallInteger, default = NO)
    projects = db.relationship('Project', backref = 'author', lazy = 'dynamic')
    member_of = db.Column(db.String(500))
    
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

    def addMemberOf(self, pid):
        if self.member_of:
            memList = self.member_of.split()
            memList.append(str(pid))
            self.member_of = ' '.join(memList)
        else:
            self.member_of = str(pid)
        db.session.commit()

    def getMemberOf(self):
        if self.member_of:
            projList = self.member_of.split()
            projList = [int(x) for x in projList]
            projects = []
            for p in projList:
                proj = Project.query.filter_by(id=p)
                if proj:
                    projects.append(proj[0])
            return projects
        else:
            return []


class Project(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    about = db.Column(db.String(400))
    help = db.Column(db.String(400))
    description = db.Column(db.String(400))
    progress = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    members = db.Column(db.String(400))


    def __repr__(self):
        return '<Project %r>' % (self.name)

    def addMember(self, uid):
        if self.members:
            memList = self.members.split()
            if str(uid) in memList:
                return False
            memList.append(str(uid))
            self.members = ' '.join(memList)
        else:
            self.members = str(uid)
        db.session.commit()
        user = User.query.filter_by(id=uid)
        user = user[0]
        user.addMemberOf(self.id)
        return True

    def getMembers(self):
        if self.members:
            memList = self.members.split()
            memList = [int(x) for x in memList]
            members = []
            for m in memList:
                user = User.query.filter_by(id=m)
                if user:
                    members.append(user[0])
            return members
        else:
            return []

