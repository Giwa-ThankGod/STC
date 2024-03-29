import bcrypt
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy

date = datetime.now()
db_string = date.strftime("%B %d, %Y | %H:%M:%S")

host = 'localhost:5432'
database_name = 'stc'
database_path = f'postgresql://postgres:August404@{host}/{database_name}'

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

    with app.app_context():
        db.create_all()

class Group(db.Model):
    __tablename__ = 'group'

    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    title = Column(String(80), unique=True)
    description = Column(String(200), nullable=True)

    def __init__(self, title, description):
        self.title = title
        self.description = description

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'user'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    username = Column(String(80), unique=True)
    password = Column(String(), nullable=False)
    first_name = Column(String(80), nullable=True)
    last_name = Column(String(80), nullable=True)
    role = Column(String(), nullable=False)

    is_superuser = Column(Boolean(create_constraint=False))
    is_staff = Column(Boolean(create_constraint=False))
    is_active = Column(Boolean(create_constraint=True))

    # Managing RBAC(Role Based Access Control)
    group = db.relationship('Group', backref=db.backref('users',lazy=True))
    group_id = Column(Integer(), ForeignKey('group.id'), nullable=True)

    def __init__(self, username, password, role, is_superuser=False, is_staff=False, is_active=True, first_name=None, last_name=None):
        self.username = username
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_superuser = is_superuser
        self.is_staff = is_staff
        self.is_active = is_active

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_authenticated(self,password):
        #Checks if user's information corresponds
        state = bcrypt.checkpw(password.encode(), self.password.encode())
        return state

    def short(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

    def long(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_superuser': self.is_superuser,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
        }

class Question(db.Model):
    __tablename__ = 'question'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    title = Column(String(80), nullable=False, unique=True)
    body = Column(String(), unique=True, nullable=False)
    tag = Column(String(150), nullable=True)
    created_on = Column(String(80))
    user = db.relationship('User', backref=db.backref('questions',lazy=True, cascade='all,delete'))
    user_id = Column(Integer(), ForeignKey('user.id'))

    def __init__(self, title, body, tag, user_id):
        self.title = title
        self.body = body
        self.tag = tag
        self.created_on = db_string
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short_format(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'tags': json.loads(self.tag),
            'created_on': self.created_on,
            'user': self.user.username,
            'user_id': self.user_id,
            'role': self.user.role
            }

    def long_format(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'tags': json.loads(self.tag),
            'created_on': self.created_on,
            'answers': [answer.format() for answer in self.answers],
            'user': self.user.username,
            'user_id': self.user_id,
            'role': self.user.role
        }

class Answer(db.Model):
    __tablename__ = 'answer'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    body = Column(String(), nullable=False)
    created_on = Column(String(80))

    question = db.relationship('Question', backref=db.backref('answers',lazy=True, cascade='all,delete'))
    question_id = Column(Integer(), ForeignKey('question.id'))

    user = db.relationship('User', backref=db.backref('answers',lazy=True, cascade='all,delete'))
    user_id = Column(Integer(), ForeignKey('user.id'))

    def __init__(self, body, question_id, user_id):
        self.body = body
        self.created_on = db_string
        self.question_id = question_id
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        # Return the upvotes and downvotes on an answer.
        upvotes, downvotes = (0, 0)

        for vote in self.votes:
            if vote.upvote:
                upvotes += 1
            else:
                downvotes += 1

        return {
            'id': self.id,
            'body': self.body,
            'created_on': self.created_on,
            'question_id': self.question_id,
            'user': self.user.username,
            'user_id': self.user_id,
            'role': self.user.role,
            'upvotes': upvotes,
            'downvotes': downvotes
        }
    
class Vote(db.Model):
    __tablename__ = 'vote'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)

    upvote = Column(Boolean(), default=False, nullable=True)
    downvote = Column(Boolean(), default=False, nullable=True)

    answer = db.relationship('Answer', backref=db.backref('votes',lazy=True, cascade='all,delete'))
    answer_id = Column(Integer(), ForeignKey('answer.id'))

    user = db.relationship('User', backref=db.backref('votes',lazy=True, cascade='all,delete'))
    user_id = Column(Integer(), ForeignKey('user.id'))

    def __init__(self, answer_id, user_id, upvote=False, downvote=False):
        self.upvote = upvote
        self.downvote = downvote
        self.answer_id = answer_id
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'upvote': self.upvote,
            'downvote': self.downvote,
            'answer_id': self.answer_id,
            'user': self.user.username,
            'user_id': self.user_id
        }
    
class Article(db.Model):
    __tablename__ = 'article'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    title = Column(String(80), nullable=False, unique=True)
    body = Column(String(), unique=True, nullable=False)
    created_on = Column(String(80))
    updated_on = Column(String(80))

    user = db.relationship('User', backref=db.backref('articles',lazy=True, cascade='all,delete'))
    user_id = Column(Integer(), ForeignKey('user.id'))

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.created_on = db_string
        self.updated_on = db_string
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short_format(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'user': self.user.username,
            'user_id': self.user_id,
            'role': self.user.role
        }