from flask import Flask
import secrets
from os import path
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"


def create_database(app):
    if not path.exists('application/' + DB_NAME):
        db.create_all(app=app)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(secrets.token_hex(128))

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    create_database(app)

    return app