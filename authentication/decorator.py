from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps


def roleCheck(role):
    def innerFunction(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            actualRole = get_jwt()["role"]
            if actualRole == role:
                return function(*args, **kwargs)
            else:
                return jsonify(msg="Missing Authorization Header"), 401

        return decorator

    return innerFunction
