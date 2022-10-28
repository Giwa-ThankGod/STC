import bcrypt
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy

date = datetime.now()
db_string = date.strftime("%B %d, %Y | %H:%M:%S")

host = 'localhost:5432'
database_name = 'stc'
database_path = f'postgresql://postgres:August@{host}/{database_name}'

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
    db.create_all()

class User(db.Model):
    __tablename__ = 'user'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    username = Column(String(80), unique=True)
    password = Column(String(), unique=True, nullable=False)
    first_name = Column(String(80), nullable=True)
    last_name = Column(String(80), nullable=True)
    role = Column(String(), nullable=False)

    def __init__(self, username, password, first_name, last_name, role):
        self.username = username
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

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
        }

    def long(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
        }

class Question(db.Model):
    __tablename__ = 'question'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    title = Column(String(80), nullable=False)
    body = Column(String(), unique=True, nullable=False)
    tag = Column(String(150), nullable=True)
    created_on = Column(String(80))
    user = db.relationship('User', backref=db.backref('user',lazy=True, cascade='all,delete'))
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

    def format(self):
        answers = Answer.query.join(Question).filter(Question.id == self.id)
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'tags': json.loads(self.tag),
            'created_on': self.created_on,
            'answers': [answer.format() for answer in answers],
            'user_id': self.user_id,
            }

class Answer(db.Model):
    __tablename__ = 'answer'

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "postgresql"), primary_key=True)
    body = Column(String(), nullable=False)
    created_on = Column(String(80))

    question = db.relationship('Question', backref=db.backref('question',lazy=True, cascade='all,delete'))
    question_id = Column(Integer(), ForeignKey('question.id'))

    def __init__(self, body, question_id):
        self.body = body
        self.created_on = db_string
        self.question_id = question_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()