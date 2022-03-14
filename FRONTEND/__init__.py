from flask import Flask
import string
import random


def generate_random_password():
    characters = string.ascii_lowercase + \
        string.ascii_uppercase + string.digits + string.punctuation
    length = int(128)
    generate = random.sample(characters, length)
    generated_password = "".join(generate)
    print('Password Generated: ' + generated_password)
    return(generated_password)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = generate_random_password
