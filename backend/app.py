import os
import json
import datetime
from flask import Flask, jsonify, abort, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from jose import jwt
from auth import AuthError, requires_auth, requires_role

from database.models import db, setup_db, User, Question, Answer

app = Flask(__name__)
setup_db(app)
#Apply Migrations
migrate = Migrate(app, db)

# db.create_all()

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + 10

    formatted_questions = [entity.short_format() for entity in selection]
    current_questions = formatted_questions[start:end]

    return current_questions

@app.route('/public', methods=['GET'])
def public():
    return jsonify({
        'message': 'Public Endpoint',
        "success": True,
    })

@app.route('/private', methods=['GET'])
@requires_auth
def private(token):
    return jsonify({'message': 'Private Endpoint','token': token})

#----------------------------------------------------------------------------#
# READ USERS.
#----------------------------------------------------------------------------#
@app.route('/users', methods=['GET'])
@requires_auth
@requires_role(roles=['manager', 'staff'])
def users(token):
    users = User.query.all()

    return jsonify({
        'success': True,
        'token': token,
        'users': [user.long() for user in users]
    })
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------#
# CREATE USER : REGISTER.
#----------------------------------------------------------------------------#
@app.route('/users', methods=['POST'])
@requires_auth
def create_user(payload):
    #grab post arguments
    body = request.get_json()

    username = body.get("username", None)
    password = body.get("password", None)
    first_name = body.get("first_name", None)
    last_name = body.get("last_name", None)
    role = body.get("role", None)

    if username is None or password is None or role is None:
        abort(400)

    try:
        user = User(
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
            role = role,
        )
        user.insert()
    except:
        abort(422)

    return jsonify({
        "success": True,
        "user": user.id,
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# UPDATE USER
#----------------------------------------------------------------------------#
@app.route('/users/<int:user_id>', methods=['PATCH'])
@requires_auth
@requires_role(roles=['manager', 'staff', 'student'])
def update_user(payload, user_id):
    user = User.query.get(user_id)

    # Restricts manager role to only update students and not others with manager role.
    if payload['role'] == 'manager' and  user.role == 'manager':
        abort(401)
    elif payload['role'] == 'manager' or payload['user']['id'] == user_id:
        body = request.get_json()

        first_name = body.get("first_name", None)
        last_name = body.get("last_name", None)
        role = body.get("role", None)

        if first_name is None or last_name is None:
            abort(400)

        try:
            user.first_name = first_name
            user.last_name = last_name
            # Only manager can update user role
            if payload['role'] == 'manager' and role:
                user.role = role
            user.update()
        except:
            abort(422)

        return jsonify({
            "success": True,
            "user": user.long(),
        })
    else:
        raise AuthError({
            'code': 'unauthorized user',
            'description': 'User is not authorized to update this user"s details.'
        }, 401)
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# DELETE USER.
#----------------------------------------------------------------------------#
@app.route('/users/<int:user_id>', methods=['DELETE'])
@requires_auth
@requires_role(roles=['manager']) 
def delete_user(token,user_id):
    try:
        user = User.query.get(user_id)
        user.delete()
    except:
        abort(404)

    return jsonify({
        'success': True,
        'user': user_id 
    })
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# LOGIN.
#----------------------------------------------------------------------------#

@app.route('/token', methods=['GET'])
def login():
    auth = request.authorization
    
    try:
        user = User.query.filter(User.username == auth.username).first()
    except:
        raise AuthError({
            "code": 'Invalid username!!!',
            "description": f'Could not find user with username {auth.username}'
        }, 422)
    
    if auth and user.is_authenticated(auth.password):
        token = jwt.encode({
            'role': user.role,
            'user': user.short(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        },os.environ['SECRET_KEY'])
        return jsonify({'token' : token})
    else:
        raise AuthError({
            'code': 'authenticaion failed',
            f'description': 'Could not authenticate user.'
        }, 401)
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# READ QUESTIONS.
#----------------------------------------------------------------------------#
@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()

    paginated_questions = paginate(request, questions)

    # if paginated_questions == []:
    #         abort(404)

    return jsonify({
        'success': True,
        'questions': paginated_questions
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# QUESTION DETAIL.
#----------------------------------------------------------------------------#
@app.route('/questions/<id>', methods=['GET'])
def question_detail(id):
    question = Question.query.filter(Question.id == id).first()

    if question is None:
        abort(404)

    return jsonify({
        'success': True,
        'question': question.long_format(),
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# CREATE QUESTIONS.
#----------------------------------------------------------------------------#
@app.route('/questions', methods=['POST'])
@requires_auth
@requires_role(roles=['manager', 'staff', 'student'])
def create_questions(token):
    #grab post arguments
    data = request.get_json()

    title = data.get("title", None)
    body = data.get("body", None)
    tags = data.get("tags", None)
    user_id = data.get("user_id", None)

    if title is None or body is None or tags is None or user_id is None:
        abort(400)

    try:
        question = Question(
            title = title,
            body = body,
            tag = json.dumps(tags),
            user_id = user_id
        )
        question.insert()
    except:
        abort(422)

    return jsonify({
        "success": True,
        "question": question.id,
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# UPDATE QUESTIONS.
#----------------------------------------------------------------------------#
@app.route('/questions/<id>', methods=['PATCH'])
@requires_auth
@requires_role(roles=['manager', 'staff', 'student'])
def update_questions(token,id):
    question = Question.query.filter(Question.id == id).first()

    # Allowing only the right user to update his/her question.
    if token['user']['id'] != question.user_id:
        abort(401)

    data = request.get_json()

    title = data.get("title", None)
    body = data.get("body", None)
    tags = data.get("tags", None)

    if title is None or body is None or tags is None:
        abort(400)

    try:
        question.title = title
        question.body = body
        question.tag = json.dumps(tags)
        question.update()
    except:
        abort(404)

    questions = Question.query.all()

    return jsonify({
        'success': True,
        'questions': [question.short_format() for question in questions]
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# DELETE QUESTIONS.
#----------------------------------------------------------------------------#
@app.route('/questions/<id>', methods=['DELETE'])
@requires_auth
@requires_role(roles=['manager', 'staff', 'student'])
def delete_questions(token):
    try:
        question = Question.query.filter(Question.id == id).first()
        # Allowing only the right user to delete his/her question.
        if token['role'] == 'manager' or token['user']['id'] == question.user_id:
            question.delete()
        else:
            abort(401)
    except:
        abort(404)

    return jsonify({
        'success': True,
        'questions': question.short_format()
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# SEARCH QUESTIONS.
#----------------------------------------------------------------------------#
@app.route('/search-questions/', methods=['GET'])
def search_questions():
    search_term = request.args.get('search', None)

    if search_term is None:
        abort(404)

    questions = Question.query.filter(
            Question.title.ilike('%'+search_term+'%') | 
            Question.body.ilike('%'+search_term+'%') |
            Question.tag.ilike('%'+search_term+'%')
        )

    return jsonify({
        'success': True,
        'search_term': search_term,
        'questions': [question.short_format() for question in questions]
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# READ ANSWERS.
#----------------------------------------------------------------------------#
@app.route('/answers/<question_id>', methods=['GET'])
def get_answers(question_id):
    try:
        answers = Answer.query.filter(question_id=question_id)
    except:
        abort(404)

    return jsonify({
        'success': True,
        'answers': [answer.format() for answer in answers],
        'count': len(answers)
    })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# CREATE ANWERS.
#----------------------------------------------------------------------------#
@app.route('/answers', methods=['POST'])
@requires_auth
@requires_role(roles=['manager', 'staff', 'student'])
def create_answers(token):
    #grab post arguments
    data = request.get_json()

    body = data.get("body", None)
    question_id = data.get("question_id", None)

    if body is None or question_id is None:
        abort(400)

    try:
        answer = Answer(    
            body = body,
            question_id = question_id
        )
        answer.insert()
    except:
        abort(422)

    return jsonify({
        "success": True,
        "token": token,
        "answer": answer.id
    })
#----------------------------------------------------------------------------#

"""
    ERROR HANDLERS
"""
@app.errorhandler(AuthError)
def autherror(AuthError):
    return jsonify({
        'success': False,
        'error': AuthError.error['code'],
        'message': AuthError.error['description'],
        }), AuthError.status_code

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad_request"
        }), 400

@app.errorhandler(401)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method_not_allowed"
        }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


if __name__ == '__main__':
    app.run(debug=True)

