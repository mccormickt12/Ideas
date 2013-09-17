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
    progress = db.Column(db.String(64))
    activated = db.Column(db.SmallInteger, default = NO)
    projects = db.relationship('Project', backref = 'author', lazy = 'dynamic')
    requests = db.relationship('Request', backref = 'owner', lazy = 'dynamic')
    following = db.Column(db.String(500))
    member_of = db.Column(db.String(400))
    
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

    def follow(self, pid):
        if self.following:
            memList = self.following.split()
            memList.append(str(pid))
            self.following = ' '.join(memList)
        else:
            self.following = str(pid)
        db.session.commit()

    def getFollowing(self):
        if self.following:
            projList = self.following.split()
            projList = [int(x) for x in projList]
            projects = []
            for p in projList:
                proj = Project.query.filter_by(id=p)
                if proj.first():
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
    following = db.Column(db.String(400))
    members = db.Column(db.String(400))
    photo_exists = db.Column(db.SmallInteger, default = NO)
    photo_file = db.Column(db.LargeBinary(1000000))
    photo_name = db.Column(db.String(64))


    def __repr__(self):
        return '<Project %r>' % (self.name)

    def addFollower(self, uid):
        if self.following:
            memList = self.following.split()
            if str(uid) in memList:
                return False
            memList.append(str(uid))
            self.following = ' '.join(memList)
        else:
            self.following = str(uid)
        db.session.commit()
        user = User.query.filter_by(id=uid)
        user = user[0]
        user.follow(self.id)
        return True

    def getFollowers(self):
        if self.following:
            memList = self.following.split()
            memList = [int(x) for x in memList]
            following = []
            print memList
            for m in memList:
                user = User.query.filter_by(id=m)
                if user.first():
                    following.append(user[0])
            return following
        else:
            return []


class Request(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    proj_id = db.Column(db.Integer)
    requester_id = db.Column(db.Integer)
    username = db.Column(db.String(64))
    skills = db.Column(db.String(400))
    reason = db.Column(db.String(400))
