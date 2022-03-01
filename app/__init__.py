from flask_cors import CORS
from flask import Flask
from yookassa import Configuration
import os

import s3fs

from . import controller, model, admin
from .config import config_by_name


def create_flask_app(config_name):
    config = config_by_name[config_name]
    app = Flask(__name__, template_folder=config.TEMPLATES_DIR)
    app.secret_key = os.urandom(24)
    app.config.from_object(config)
    return app


def create_app(config_name):
    app = create_flask_app(config_name)
    # app.fs = s3fs.S3FileSystem(anon=False,
    #                            client_kwargs={
    #                              'endpoint_url': app.config['S3_URL']})
    # CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
    controller.init_app(app)
    model.init_app(app)
    admin.init_app(app)
    return app

