import click
import logging
import os
from flask import request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app import create_app
from app.model import db, entity, User, Staff

logging.basicConfig(filename="logs/basic_log.txt",
                    level=logging.INFO,
                    filemode='a',
                    format='%(asctime)s %(levelname)s-%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


app = create_app(os.getenv('SERVER_ENV') or 'dev')
jwt = JWTManager(app)
migrate = Migrate(app, db, compare_type=True)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    if app.config['LOG_ERRORS'] and response.status_code >= 400:
        app.logger.error("Request url: {request_url}\n"
                         "Request headers: {request_headers}\n"
                         "Request data: {request_data}\n"
                         "Response status: {response_status}\n"
                         "Response data: {response_data}".format(request_url=request.url,
                                                                 request_data=request.get_data(),
                                                                 request_headers=request.headers,
                                                                 response_status=response.status,
                                                                 response_data=response.get_data()))

    return response


@app.cli.command()
def resetdb():
    db.drop_all()
    db.create_all()


@app.cli.command()
def createdb():
    db.create_all()


@app.cli.command('generate')
@click.argument('count')
@click.argument('model_name')
def generate_data(count, model_name):
    if hasattr(entity, model_name):
        cls = getattr(entity, model_name)
        cls().generate_fake_data(count=int(count))
    else:
        print('No such model')
