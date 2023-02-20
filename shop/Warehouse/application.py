from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager
from shop.configuration import Configuration
from shop.models import *
from authentication.decorator import roleCheck
from redis import Redis
import io
import csv

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@roleCheck("worker")
def update():
    file = request.files.get('file', None)
    if not file:
        return jsonify(message="Field file missing."), 400
    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    with Redis(host=Configuration.REDIS_HOST, decode_responses=True, port=6379) as redis:
        line = 0

        for row in reader:
            if len(row) < 4:
                return jsonify(message=f"Incorrect number of values on line {line}."), 400
            try:
                if float(row[3]) <= 0:
                    return jsonify(message=f"Incorrect price on line {line}."), 400
            except ValueError as error:
                return jsonify(message=f"Incorrect price on line {line}."), 400
            try:
                if int(row[2]) <= 0:
                    return jsonify(message=f"Incorrect quantity on line {line}."), 400
            except ValueError as error:
                return jsonify(message=f"Incorrect quantity on line {line}."), 400

            line += 1

        redis.rpush(Configuration.REDIS_LIST, content)

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=Configuration.WAREHOUSE_PORT)
