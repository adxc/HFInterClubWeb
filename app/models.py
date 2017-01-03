from . import db, login_manager
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from markdown import markdown
import bleach


class User(UserMixin, db.Model):

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=1)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=True)
    create_time = db.Column(db.Date, nullable=False,default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=False)
    email_confirm = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.email_confirm = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=1)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
                 'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES |
                               Permission.MODERATE_COMMENTS, False),
                 'Administrator': (0xff, False)}

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Permission:
    FOLLOW = 0x01                        # 关注用户
    COMMENT = 0x02                       # 发表评论
    WRITE_ARTICLES = 0x04                # 写文章
    MODERATE_COMMENTS = 0x08             # 管理评论
    ADMINISTER = 0x80                    # 管理网站


login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=1)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags,
                                                       strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=1)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags,
                                                       strip=True))

db.event.listen(Comment.body, 'set', Comment.on_change_body)


class Hfmatch(db.Model):
    __tablename__ = 'hfmatch'
    id = db.Column(db.Integer, primary_key=True, autoincrement=1)
    date = db.Column(db.Date, nullable=False)
    competitor = db.Column(db.String(45), nullable=False)
    score = db.Column(db.String(45), nullable=False)
    shooter = db.Column(db.String(45))
    assist = db.Column(db.String(45))
    excellent = db.Column(db.String(45))
