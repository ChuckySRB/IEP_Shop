from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database
from sqlalchemy_utils import database_exists, create_database
import os

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if __name__ == "__main__":
    done = False
    while not done:
        try:
            if not database_exists(Configuration.SQLALCHEMY_DATABASE_URI):
                create_database(Configuration.SQLALCHEMY_DATABASE_URI)
            database.init_app(application)

            with application.app_context() as context:
                init()
                migrate(message="Initial migration.")
                upgrade()

                done = True

        except Exception as error:
            print(error)

