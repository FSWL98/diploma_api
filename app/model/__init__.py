from .db import db
from .entity import *
from .relation import *


def init_app(app):
    db.init_app(app)
