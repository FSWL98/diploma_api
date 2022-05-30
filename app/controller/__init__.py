from datetime import datetime
from os import environ

from flask import Blueprint, url_for
from flask_restx import Api, fields
from flask_restx.apidoc import apidoc
from jsonschema import FormatChecker

from . import auth_controller
from . import criteria_controller
from . import default_controller
from . import event_controller
from . import mark_controller
from . import pairing_mark_controller
from . import solution_controller
from . import staff_controller
from . import user_controller
from ..util import get_version


def validate_datetime(instance):
    if not isinstance(instance, str):
        return False
    return fields.date_from_iso8601(instance)


def validate_time_hm(instance):
    if not isinstance(instance, str):
        return False
    return datetime.strptime(instance, '%H:%M')


FormatChecker.cls_checks('date-time', ValueError)(validate_datetime)
FormatChecker.cls_checks('time-hm', ValueError)(validate_time_hm)


class ApiScheme(Api):
    @property
    def specs_url(self):
        scheme = environ['SCHEME']
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


AUTHORIZATIONS = {
    'access-token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
    }
}


def init_app(app):
    apidoc.url_prefix = app.config['URL_PREFIX']
    blueprint = Blueprint('api', __name__, url_prefix=app.config['URL_PREFIX'])
    api = ApiScheme(blueprint, version=get_version(), title='Diploma API', description='API for Diploma',
                    doc=app.config['DOC_URL'], authorizations=AUTHORIZATIONS,
                    format_checker=FormatChecker(formats=['date-time', 'date', 'time-hm']))

    api.add_namespace(default_controller.api, path='/')
    api.add_namespace(auth_controller.api)
    api.add_namespace(criteria_controller.api, path='/criteria')
    api.add_namespace(event_controller.api, path='/event')
    api.add_namespace(mark_controller.api, path='/mark')
    api.add_namespace(pairing_mark_controller.api, path='/pairing_mark')
    api.add_namespace(solution_controller.api, path='/solution')
    api.add_namespace(staff_controller.api, path='/staff')
    api.add_namespace(user_controller.api, path='/user')

    app.register_blueprint(blueprint)
