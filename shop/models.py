from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "products_categories"

    id = database.Column(database.Integer, primary_key=True)
    product = database.Column(database.ForeignKey("products.id"), nullable=False)
    category = database.Column(database.ForeignKey("categories.id"), nullable=False)


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Integer, nullable=False)
    available_amount = database.Column(database.Integer, default=0)
    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")

    def dict(self):
        return {"categories": [category.name for category in self.categories],
                "id": self.id,
                "name": self.name,
                "price": self.price,
                "available_amount": self.available_amount}


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)

    user = database.Column(database.String(256), nullable=False)
    ordered_products = database.relationship("OrderedProduct", back_populates="order")
    total_price = database.Column(database.Integer, primary_key=True)
    status = database.Column(database.String(256), nullable=False)
    date_created = database.Column(database.TIMESTAMP, nullable=False)


class OrderedProduct(database.Model):
    __tablename__ = "ordered_products"

    id = database.Column(database.Integer, primary_key=True)

    productID = database.Column(database.ForeignKey("products.id"), nullable=False)
    requested = database.Column(database.Integer, nullable=False)
    received = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)

    orderID = database.Column(database.ForeignKey("orders.id"), nullable=False)
    order = database.relationship("Order", back_populates="ordered_products")

    def dict(self):
        product = Product.query.filter(Product.id == self.productID).first()
        categories = [category.name for category in Category.query.join(ProductCategory) \
            .filter(ProductCategory.product == product.id)]

        return {"categories": categories, "name": product.name, "price": self.price,
                "received": self.received, "requested": self.requested}
