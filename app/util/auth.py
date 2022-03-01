import copy
from datetime import datetime
from functools import wraps
from http import HTTPStatus

from flask import request

from .functions import handle_error
from ..model import UserStaff
from ..model.entity.api_key import ApiKey
from ..model.entity.person import Person
from ..model.entity.staff import Staff
from ..model.entity.user import User


def role_access_required(role_name):
    def outer_decorated(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            roles = [role_name] if not isinstance(role_name, list) else role_name
            api = args[0].api
            if request.environ.get('staff_id') is None:
                if request.environ.get('user_id') and 'user' in roles:
                    return f(*args, **kwargs)
                api.abort(HTTPStatus.FORBIDDEN, f'{", ".join(roles)} access required')
            staff = Staff.get_staff_instance_by_id(request.environ['staff_id'])
            if staff.has_role('admin'):
                return f(*args, **kwargs)
            for role in roles:
                if staff.has_role(role):
                    return f(*args, **kwargs)
            api.abort(HTTPStatus.FORBIDDEN, f'{", ".join(roles)} access required')

        return decorated

    return outer_decorated


def access_token_required(is_access_token=True):
    def outer_decorated(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            api = args[0].api
            if 'authorization' not in request.headers:
                api.abort(HTTPStatus.UNAUTHORIZED, 'Access token required')

            if is_access_token:
                access_token = get_access_token()
            else:
                access_token = get_password_reset_token()
            token = handle_error(Person.decode_access_token(access_token), api, HTTPStatus.UNAUTHORIZED)
            if is_access_token and token['sub']['refresh']:
                api.abort(HTTPStatus.UNAUTHORIZED, 'Refresh token supplied instead of access token')
            if not is_access_token and not token['sub']['password']:
                api.abort(HTTPStatus.UNAUTHORIZED, 'Access or refresh token provided instead of password token')

            request.environ['token'] = access_token
            request.environ['person_id'] = token['sub']['person_id']
            request.environ['user_id'] = token['sub']['user_id']
            request.environ['staff_id'] = token['sub']['staff_id']
            return f(*args, **kwargs)

        return decorated
    return outer_decorated


def password_reset_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api = args[0].api
        if 'authorization' not in request.headers:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Access token required')
        password_reset_token = get_password_reset_token()

        token = handle_error(Person.decode_access_token(password_reset_token), api, HTTPStatus.UNAUTHORIZED)
        if not token['sub']['password']:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Access or refresh token provided instead of password token')
        request.environ['token'] = password_reset_token
        request.environ['person_id'] = token['sub']['person_id']
        request.environ['user_id'] = token['sub']['user_id']
        request.environ['staff_id'] = token['sub']['staff_id']
        return f(*args, **kwargs)

    return decorated


def get_access_token():
    return request.headers['authorization'].split()[-1]


def get_password_reset_token():
    return request.headers['authorization'].split()[-1]


def is_valid_password(password):
    min_len, max_len = 8, 33
    symbols = ['!', '.', '?', '(', ')', ',', '@', '#', '$', '%', '^', '&', '*', '\"', '\'', '/', '\\', '[', ']', '{', '}', '<', '>', '=', '-', '+', '_', '|', ':', ';', '~']
    if not min_len < len(password) < max_len:
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in symbols for char in password):
        return False
    return True


def add_last_change_by_id(data, deep=True):
    if 'person_id' not in request.environ:
        return data
    if deep:
        new_data = copy.deepcopy(data)
    else:
        new_data = data.copy()
    new_data.update({'last_change_by_id': request.environ['person_id']})
    return new_data


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api = args[0].api
        if 'authorization' not in request.headers:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Access token required')
        access_token = get_access_token()
        token = ApiKey.get_api_key_by_key(access_token)
        if token is None:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Invalid token supplied')
        expire_date = datetime.strptime(token['expire_date'], '%Y-%m-%dT%H:%M:%S')
        if expire_date.timestamp() < datetime.utcnow().timestamp():
            ApiKey.delete(token['key'])
            api.abort(HTTPStatus.UNAUTHORIZED, 'Expired token')
        request.environ['role_id'] = token['role_id']
        return f(*args, **kwargs)

    return decorated


def check_user_staff_access(api, user_id, abort=True):
    if is_doctor(request.environ['staff_id']) and not UserStaff.get_relation(user_id, request.environ['staff_id']):
        if abort:
            api.abort(HTTPStatus.FORBIDDEN, "This user is not related to the staff person!")
        return False
    return True


def is_partner(staff_id):
    staff = Staff.get_staff_instance_by_id(staff_id)
    return staff.has_role('partner')


def is_doctor(staff_id):
    staff = Staff.get_staff_instance_by_id(staff_id)
    return staff.has_role('doctor')


def get_user_from_token(api_):
    if 'user_id' not in request.environ or request.environ['user_id'] is None:
        api_.abort(HTTPStatus.UNAUTHORIZED, 'Invalid token supplied')
    user = User.get_user_by_id(request.environ['user_id'])
    if not user:
        api_.abort(HTTPStatus.UNAUTHORIZED, 'User not found')
    return user


def get_staff_from_token(api_):
    if 'staff_id' not in request.environ or request.environ['staff_id'] is None:
        api_.abort(HTTPStatus.UNAUTHORIZED, 'Invalid token supplied')
    staff = Staff.get_staff_by_id(request.environ['staff_id'])
    if not staff:
        api_.abort(HTTPStatus.UNAUTHORIZED, 'Staff not found')
    return staff
