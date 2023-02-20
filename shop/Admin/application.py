from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from shop.configuration import Configuration
from shop.models import *
from math import trunc
from authentication.decorator import roleCheck
from sqlalchemy import func, desc


application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/productStatus", methods=["GET"])
@roleCheck("admin")
def product_status():
    products = Product.query.join(OrderedProduct).group_by(Product.name).with_entities(Product.name, func.sum(
        OrderedProduct.requested), func.sum(OrderedProduct.requested) - func.sum(OrderedProduct.received)).having(
        func.sum(OrderedProduct.received) > 0).all()

    stats = []
    for product in products:
        stats.append({
            "name": product[0],
            "sold": trunc(product[1]),
            "waiting": trunc(product[2]),
        })

    return jsonify(statistics=stats), 200


@application.route("/categoryStatus", methods=["GET"])
@roleCheck("admin")
def category_status():
    categories = Category.query.join(ProductCategory).join(Product).outerjoin(OrderedProduct).group_by(
        Category.name).with_entities(Category.name, func.sum(OrderedProduct.requested)).order_by(
        desc(func.sum(OrderedProduct.requested)), Category.name).all()

    stats = []
    for categorie in categories:
        stats.append(categorie[0])

    return jsonify(statistics=stats), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=Configuration.ADMIN_PORT)
