from flask import Flask
from redis import Redis
from configuration import Configuration
from models import *

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)

with Redis(host=Configuration.REDIS_HOST, decode_responses=True, port=6379) as redis:
    while True:
        with application.app_context() as context:

            # Waiting a message from warehouse
            bytes = redis.lpop(Configuration.REDIS_LIST)
            if bytes is None:
                continue

            content = bytes
            orders = content.split("\n")

            for order in orders:

                order_elems = order.split(",")
                categories = order_elems[0].split("|")
                name = order_elems[1]
                new_amount = int(order_elems[2])
                price = float(order_elems[3])

                product = Product.query.filter(Product.name == name).first()

                if not product:
                    # New Product
                    product = Product(name=name, price=price, available_amount=new_amount)
                    database.session.add(product)
                    database.session.commit()

                    for category in categories:

                        cat = Category.query.filter(Category.name == category).first()
                        if not cat:
                            # Adding category
                            cat = Category(name=category)
                            database.session.add(cat)
                            database.session.commit()

                        pc = ProductCategory(product=product.id, category=cat.id)
                        database.session.add(pc)
                        database.session.commit()

                else:
                    # Validating Order
                    productCategories = ProductCategory.query.filter(ProductCategory.product == product.id).all()
                    createdCategories = []
                    for pc in productCategories:
                        createdCategories.append(Category.query.filter(Category.id == pc.category).first().name)

                    if len(categories) != len(createdCategories):
                        continue
                    skip = False

                    for cat in categories:
                        if cat not in createdCategories:
                            skip = True
                            break
                    if skip:
                        continue

                    newPrice = (product.available_amount * product.price + new_amount * price) / (
                                product.available_amount + new_amount)
                    product.price = newPrice
                    wasntZero = product.available_amount != 0
                    newAmount = product.available_amount + new_amount
                    product.available_amount = newAmount

                    database.session.commit()

                    if wasntZero:
                        continue

                    pendingOrders = Order.query.filter(Order.status == "PENDING").all()

                    if len(pendingOrders) == 0:
                        continue

                    # Compliting pending orders
                    pendingOrders.sort(key=lambda k: k.date_created)

                    for i in range(len(pendingOrders)):
                        o = pendingOrders[i]
                        ordreq = OrderedProduct.query.filter(OrderedProduct.orderID == o.id).all()
                        completed = True
                        for j in range(len(ordreq)):
                            p = ordreq[j]
                            if p.productID == product.id and newAmount > 0:
                                if p.required > p.received:
                                    amount = p.required - p.received
                                    p.received = p.received + newAmount if amount > newAmount else p.required
                                    newAmount -= amount
                            if p.required > p.received:
                                completed = False
                        if completed:
                            o.status = "COMPLETE"
                        if newAmount <= 0:
                            newAmount = 0
                            break

                    product.available_amount = newAmount
                    database.session.commit()
            print("Did Something!")
