
### Getting Started

# BACKEND SETUP

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./backend` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=api.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## API Reference

### Getting Started with the API
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`. 
- Authentication: This version of the application requires jwt authentication. 
Get access token by visting the domain `https://127.0.0.1:5000/token` with a valid username and password.

-sample: `curl -X POST -u Pascal:Pascal123$ http://127.0.0.1:5000/token`

```
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlcyI6Im1hbmFnZXIiLCJleHAiOjE2NjY4Nzc4Nzd9.sLPGnmYkJmGgX9aAlKflrol0Rd4cVJX0OedJuifYYds"
}
```

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return Six error types when requests fail:
- 400: Bad Request
- 401: Unauthorized Access
- 404: Resource Not Found
- 405: Method Not Allowed
- 422: Not Processable
- AuthError: Custom Error Class

### Endpoints
#### GET /questions
- Public:
    - Returns a list of 10 question objects, success value, and total number of questions
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1. 
        - Sample: `curl http://127.0.0.1:5000/questions?page=2`

- Sample: `curl http://127.0.0.1:5000/questions`

```
{
    "questions": [
        {
            "body": "I am having issues with creating my virtual environment",
            "created_on": "October 24, 2022 | 22:48:29",
            "id": 1,
            "tags": [
                "python",
                "programming"
            ],
            "title": "How to create a python virtual environment",
            "user_id": 13
        },
        {
            "body": "My django project is giving me this error, template does not exist. Please help me!!!",
            "created_on": "October 25, 2022 | 23:06:23",
            "id": 2,
            "tags": [
                "python",
                "django",
                "template"
            ],
            "title": "Django Template does not exit!!!",
            "user_id": 14
        }
    ],
    "success": true
}
```


#### GET /users
- Private:
    - Requires a valid jwt token.
    - Authorization token must contain the permission 'patch:drinks'.
    - Returns the logged in users token with a list of users with a shortend information about users

- Sample: `curl http://127.0.0.1:5000/users`

```
{
    "success": true,
    "token": {
        "exp": 1666877877,
        "roles": "manager"
    },
    "users": [
        {
            "first_name": "Ovie",
            "id": 5,
            "last_name": "Ovie",
            "password": "$2b$12$QJMBB4LiJ64xABx2EcoJduhUzIlSw.2V2mtVXgxPTBM39sippHpRa",
            "role": "manager",
            "username": "Ovie"
        },
        {
            "first_name": "Collins",
            "id": 9,
            "last_name": "Collins",
            "password": "$2b$12$YTHuERjqDLp4LOo7GfmPJeQizmbWwTyMLPiLW2GyepJADsBPFz9e2",
            "role": "staff",
            "username": "Collins"
        },
        {
            "first_name": "Marvelous",
            "id": 10,
            "last_name": "Marvelous",
            "password": "$2b$12$I8JivJ8NNIixB5noTUOkiO87EvrQ9fCd/ESWdGMYQCAvNnlQbcN1i",
            "role": "staff",
            "username": "Marvelous"
        },
        {
            "first_name": "Love",
            "id": 12,
            "last_name": "Love",
            "password": "$2b$12$tVfuyvA.kPobQgeCFEKZNOzJRs5tWyXvrdv36rBqz4645VXS2bhHm",
            "role": "manager",
            "username": "Love"
        },
        {
            "first_name": "Pascal",
            "id": 13,
            "last_name": "Pascal",
            "password": "$2b$12$9BhTS0DCrUINWOvVxRZl.uttuQeIPlHO/HfCXU6d3UVvfIQd9p99O",
            "role": "student",
            "username": "Pascal"
        },
        {
            "first_name": "Levi",
            "id": 14,
            "last_name": "Levi",
            "password": "$2b$12$mhSPMxdCwnIoYhuMxoUdLOuiMTb6btIOniHBY4f83/ov.1XqSZ4Se",
            "role": "student",
            "username": "Levi"
        }
    ]
}
```

/questions?search=gam
Note: search string has no quote surrounding it