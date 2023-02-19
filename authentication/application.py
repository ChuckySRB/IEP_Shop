from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User
from email.utils import parseaddr
import re
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from decorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/register", methods=["POST"])
def register():
    # Geting Fields
    forename = request.json.get('forename', '')
    if len(forename) == 0 or len(forename) > 256:
        return Response(jsonify(message="Field forename is missing."), 400)
    surname = request.json.get('surname', '')
    if len(surname) == 0 or len(surname) > 256:
        return Response(jsonify(message="Field surname is missing."), 400)
    email = request.json.get('email', '')
    if len(email) == 0 or len(email) > 256:
        return Response(jsonify(message="Field email is missing."), 400)
    password = request.json.get('password', '')
    if len(password) == 0 or len(password) > 256:
        return Response(jsonify(message="Field password is missing."), 400)
    isCustomer = request.json.get('isCustomer', None)
    if isCustomer == None:
        return Response(jsonify(message="Field isCustomer is missing."), 400)

    # Validation
    if not re.compile("^\w+@\w+\.com$").match(email):
        return Response(jsonify(message="Invalid email."), 400)

    if len(password) < 8 or not re.compile("[a-z]+").search(password) or not re.compile("[a-z]+").search(
            password) or not re.compile("\d+").search(password):
        return Response(jsonify(message="Invalid password."), 400)

    registeredUser = User.query.filter(User.email == email).first()
    if registeredUser:
        return Response(jsonify(message="Email already exists."), 400)

    # Registration
    if isCustomer:
        role = "customer"
    else:
        role = "worker"

    user = User(email=email, password=password, forename=forename, surname=surname, role=role)
    database.session.add(user)
    database.session.commit()

    return Response(status=200)


@application.route("/login", methods=["POST"])
def login():
    # Geting Fields
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    if len(email) == 0 or len(email) > 256:
        return Response("Field email is missing.", status=400)
    if len(password) == 0 or len(password) > 256:
        return Response("Field password is missing.", status=400)

    # Validation
    if not re.compile("^\w+@\w+\.com$").match(email):
        return Response(jsonify(message="Invalid email."), 400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return Response("Invalid credentials!", status=400)

    # Creating Token
    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"]
    }

    return Response(jsonify(create_access_token(identity=identity, additional_claims=additionalClaims), status=200))


@application.route("/", methods=["GET"])
def index():
    return "Servis za autentifikaciju!"


@application.route("/delete", methods=["POST"])
@roleCheck("admin")
def delete():
    # Geting Fields
    email = request.json.get("email", "")

    if len(email) == 0 or len(email) > 256:
        return Response("Field email is missing.", status=400)

    # Validation
    if not re.compile("^\w+@\w+\.com$").match(email):
        return Response(jsonify(message="Invalid email."), 400)

    user = User.query.filter(User.email == email).first()
    if not user:
        return Response("Invalid credentials!", status=400)

    # Deleting
    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
