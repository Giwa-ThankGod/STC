import os
from flask import request,abort
from jose import jwt
from secrets import token_urlsafe
from functools import wraps
import hashlib

#Generates a random URL-safe text string, in Base64 encoding.
os.environ['SECRET_KEY'] = token_urlsafe(20)

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    if not request.headers:
        raise AuthError({
            'code': 'header_missing',
            'description': 'Header is expected.'
        }, 401)

    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

def check_roles(roles, payload):
    if 'role' not in payload:
        raise AuthError({
            "code": 'role_not_included',
            "description": 'Persmission string is expected'
        }, 401)
    
    if payload['role'] not in roles:
        raise AuthError({
            "code": 'invalid_role_string',
            "description": f'Persmission string "{payload["role"]}" not found in {roles}'
        }, 403)

    return True

def verify_decode_jwt(token):
    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'])
        return payload
    except Exception:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.',
        }, 401)
    



def requires_auth(f):
    @wraps(f)
    def decorator(*args,**kwargs):

        token = get_token_auth_header()        
        data = verify_decode_jwt(token)

        return f(data,*args, **kwargs)
    
    return decorator


def requires_role(roles=[]):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_roles(roles, payload)
            return f(*args, **kwargs)

        return wrapper
    return requires_auth_decorator