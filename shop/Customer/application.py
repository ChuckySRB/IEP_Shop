from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity
from shop.configuration import Configuration
from shop.models import *
from authentication.decorator import roleCheck
from sqlalchemy import and_, or_
import datetime
import random

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@roleCheck("customer")
def search():
    name = request.args.get("name", "")
    category = request.args.get("category", "")

    productSearch = Product.query.join(ProductCategory).join(Category).filter(
        and_(Product.name.like(f"%{name}%"), or_(Category.name.like(f"%{category}%")))).all()

    products = []
    categories = []
    for p in productSearch:
        products.append(p.dict())
        for c in p.categories:
            categories.append(c.name)

    return jsonify(categories=categories, products=products)


@application.route("/order", methods=["POST"])
@roleCheck("customer")
def order():
    # Validation
    requests = request.json.get("requests", None)

    if not requests or len(requests) == 0:
        return jsonify(message="Field requests is missing.")

    orders = []
    for i in range(len(requests)):
        req = requests[i]
        try:
            id = int(req["id"])
        except ValueError as error:
            return jsonify(message=f"Invalid product id for request number {i}."), 400
        except KeyError as error:
            return jsonify(message=f"Product id is missing for request number {i}."), 400
        try:
            order_amount = int(req["quantity"])
        except ValueError as error:
            return jsonify(message=f"Invalid product quantity for request number {i}."), 400
        except KeyError as error:
            return jsonify(message=f"Product quantity is missing for request number {i}."), 400

        if id <= 0:
            return jsonify(message=f"Invalid product id for request number {i}."), 400
        if order_amount <= 0:
            return jsonify(message=f"Invalid product quantity for request number {i}."), 400

        product = Product.query.filter(Product.id == id).first()
        if product is None:
            return jsonify(message=f"Invalid product for request number {i}."), 400

        orders.append([id, order_amount])

    # Making Order
    order = Order(user=get_jwt_identity(), status="PENDING", total_price=0, date_created=datetime.datetime.utcnow(), id = random.randint(0,100000))
    database.session.add(order)
    database.session.commit()

    # Making magic happen
    completed = True
    for o in orders:
        id = o[0]
        o_amount = o[1]

        product = Product.query.filter(Product.id == id).first()
        order.total_price += o_amount * product.price

        received_amount = product.available_amount if o_amount >= product.available_amount else product.available_amount - o_amount
        product.available_amount -= received_amount
        if received_amount < o_amount:
            completed = False

        orp = OrderedProduct(
            productID=id,
            requested=o_amount,
            received=received_amount,
            orderID=order.id,
            price=product.price
        )

        database.session.add(orp)
        database.session.commit()

    order.status = "COMPLETE" if completed else "PENDING"
    database.session.commit()

    return jsonify(id=order.id)


@application.route("/status", methods=["GET"])
@roleCheck("customer")
def status():
    orders = Order.query.filter(Order.user == get_jwt_identity()).all()
    ordersRet = []
    for order in orders:
        my_orders = OrderedProduct.query.filter(OrderedProduct.orderID == order.id).all()
        products = []
        for my_order in my_orders:
            products.append(my_order.dict())
        ordersRet.append({
            "products": products,
            "price": order.total_price,
            "status": order.status,
            "timestamp": str(order.date_created.isoformat(sep="T", timespec="seconds")) + 'Z'
        })

    return jsonify(orders=ordersRet), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=Configuration.CUSTOMER_PORT)
