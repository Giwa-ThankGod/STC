import bcrypt
import json
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy

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
    time_stamp = Column(String(80))
    user = db.relationship('user', backref=db.backref('questions',lazy=True, cascade='all,delete'))
    user_id = Column(String(), ForeignKey('user.id'))

    def __init__(self, title, body, tag, user_id):
        self.title = title
        self.body = body
        self.tag = tag
        self.user_id = user_id