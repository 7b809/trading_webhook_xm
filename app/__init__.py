from flask import Flask
from app.routes import webhook

def create_app():
    app = Flask(__name__)
    app.register_blueprint(webhook)
    return app
