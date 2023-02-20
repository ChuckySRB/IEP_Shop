from datetime import timedelta


class Configuration:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/shop"
    REDIS_HOST = "localhost"
    REDIS_LIST = "Warehouse_List"
    JWT_SECRET_KEY = "dont_tell_anyone"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    CUSTOMER_PORT = 5001
    WAREHOUSE_PORT = 5002
    ADMIN_PORT = 5003
