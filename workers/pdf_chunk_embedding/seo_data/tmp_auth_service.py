from flask import jsonify, request
import jwt
import datetime
from functools import wraps
import traceback
from dbhandlers import auth_session
from constants import jwt_secret


# Define the JWT required decorator
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"message": "Authorization token is missing"}), 401
        try:
            payload = jwt.decode(token, jwt_secret,
                                 audience="bot:hrsupport", algorithms=["HS256"])
            entry = auth_session.get(session_id=payload['session_id'])
            exp_date = datetime.datetime.fromisoformat(entry['expDate'])
            if entry is None or 'expDate' not in entry or \
                    datetime.datetime.utcnow() > exp_date:
                return jsonify({"message": "Expired token"}), 401
        except jwt.InvalidTokenError as e:
            print(traceback.print_exc())
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


# Define the login resource to generate JWT tokens
def generate_token():
    data = request.get_json()
    user_agent = request.headers.get("User-Agent")
    # Check if the username and password are valid
    if data['username'] != 'redbusassistant' or data['password'] != 'askr2d2':
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate the JWT payload with the required claims
    payload = {
        "sub": data['username'],
        "aud": ["bot:hrsupport"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        "expDate": (datetime.datetime.utcnow() + datetime.timedelta(minutes=60)).isoformat(),
        "userAgent": user_agent,
    }
    session_id = auth_session.insert_session_record(entry=payload)
    payload['session_id'] = str(session_id.inserted_id)

    # Generate the JWT token using the PyJWT library
    jwt_token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return jsonify({"access_token": jwt_token})
