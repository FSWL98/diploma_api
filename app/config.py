import os
import socket
from datetime import timedelta

from os import environ as env


class Config:
    ROOT = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False
    SQLALCHEMY_URI = f'postgresql://{env["DB_USER"]}:{env["DB_PASSWD"]}@{env["DB_HOST"]}:{env["DB_PORT"]}'
    SQLALCHEMY_DATABASE_URI = f'{SQLALCHEMY_URI}/{env["DB_NAME"]}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_UI_REQUEST_DURATION = True
    ERROR_404_HELP = False
    CORS_SUPPORTS_CREDENTIALS = True

    HOST = f'{env["SCHEME"]}://{env["HOST"]}'
    IP = env.get('IP', socket.gethostbyname(env["HOST"].split(':')[0]))

    API_TOKEN_DAYS_ACTIVE = 7
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=600)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_SECRET_KEY = env["SECRET_KEY"]

    TEMPLATES_DIR = '../templates'
    FLASK_ADMIN_SWATCH = 'sandstone'
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_POST_REGISTER_VIEW = '/admin/'
    SECURITY_REGISTERABLE = True
    SECURITY_POST_LOGOUT_VIEW = '/admin/'
    SECURITY_POST_LOGIN_VIEW = '/admin/'
    SECURITY_PASSWORD_SALT = env["SECURITY_PASSWORD_SALT"]

    AVATARS_PATH = 'avatars'
    USER_FILE_PATH = 'user_files'

    IMAGES_DIR = './data/images'
    AUDIOS_DIR = './data/audios'
    VIDEOS_DIR = './data/videos'
    DOCUMENTS_DIR = './data/documents'

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    MAX_AUDIO_SIZE = 100 * 1024 * 1024
    MAX_DOCUMENT_SIZE = 100 * 1024 * 1024
    MAX_IMAGE_SIZE = 200 * 1024 * 1024
    MAX_VIDEO_SIZE = 200 * 1024 * 1024

    MAX_FIELD_LENGTH = 80

    API_TEMPLATES_DIR = './api_templates'


class DevelopmentConfig(Config):
    DEV = True
    URL_PREFIX = '/api/v1'
    DOC_URL = '/swagger'
    LOG_ERRORS = True


class ProductionConfig(Config):
    DEV = False
    URL_PREFIX = '/api/v1'
    DOC_URL = False
    LOG_ERRORS = True


class ProductionOnDevelopmentConfig(ProductionConfig):
    DOC_URL = DevelopmentConfig.DOC_URL


config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig,
    prod_on_dev=ProductionOnDevelopmentConfig
)
