from flask import Flask
import secrets


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(secrets.token_hex(128))

    return app
