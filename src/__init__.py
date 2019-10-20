from flask import Flask, Blueprint
from flask_script import Manager

from src.config import config_by_name

blueprint = Blueprint('api', __name__, url_prefix='/bigcorp')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.register_blueprint(blueprint)
    app.app_context().push()
    manager = Manager(app)

    return app, manager
