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

email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


@application.route("/register", methods=["POST"])
def register():
    # Geting Fields
    forename = request.json.get('forename', '')
    if type(forename)!=str or len(forename) == 0 or len(forename) > 256:
        return jsonify(message="Field forename is missing."), 400
    surname = request.json.get('surname', '')
    if type(surname)!=str or len(surname) == 0 or len(surname) > 256:
        return jsonify(message="Field surname is missing."), 400
    email = request.json.get('email', '')
    if type(email)!=str or len(email) == 0 or len(email) > 256:
        return jsonify(message="Field email is missing."), 400
    password = request.json.get('password', '')
    if type(password)!=str or len(password) == 0 or len(password) > 256:
        return jsonify(message="Field password is missing."), 400
    isCustomer = request.json.get('isCustomer', None)
    if type(isCustomer)!=bool or isCustomer == None:
        return jsonify(message="Field isCustomer is missing."), 400

    # Validation
    if not email_regex.match(email):
        return jsonify(message="Invalid email."), 400

    if len(password) < 8 or not re.compile("[a-z]+").search(password) or not re.compile("[a-z]+").search(
            password) or not re.compile("\d+").search(password):
        return jsonify(message="Invalid password."), 400

    registeredUser = User.query.filter(User.email == email).first()
    if registeredUser:
        return jsonify(message="Email already exists."), 400

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
    if type(email)!=str or len(email) == 0 or len(email) > 256:
        return jsonify(message="Field email is missing."), 400
    if type(password)!=str or (password) == 0 or len(password) > 256:
        return jsonify(message="Field password is missing."), 400

    # Validation
    if not email_regex.match(email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return jsonify(message="Invalid credentials!"), 400

    # Creating Token
    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "role": user.role,
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

    return jsonify(create_access_token(identity=identity, additional_claims=additionalClaims)), 200


@application.route("/", methods=["GET"])
def index():
    return "Servis za autentifikaciju!"


@application.route("/delete", methods=["POST"])
@roleCheck("admin")
def delete():
    # Geting Fields
    email = request.json.get("email", "")

    if type(email)!=str or len(email) == 0 or len(email) > 256:
        return jsonify(message = "Field email is missing."), 400

    # Validation
    if not email_regex.match(email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify(message="Invalid credentials!"), 400

    # Deleting
    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=5004)
