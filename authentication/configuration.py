from datetime import timedelta


class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3307/authentication"
    MIGRATIONS_PATH = "/Users/aki/PycharmProjects/projekatIEP/authentication/migrations"
    JWT_SECRET_KEY = "dont_tell_anyone"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
