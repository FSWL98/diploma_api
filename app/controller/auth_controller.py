from flask import request
from flask_restx import Resource
from flask_security.utils import verify_password
from http import HTTPStatus

from ..model.entity.staff import Staff
from ..model.entity.person import Person
from ..model.entity.user import User
from ..util.auth import add_last_change_by_id, access_token_required, is_valid_password
from ..util.dto import AuthDto, UserDto
from ..util.functions import handle_error
from ..util.mail import is_valid_email

api = AuthDto.api


def get_user(phone, email, abort=True):
    user = None
    if phone:
        user = User.get_user_by_phone(phone)
    elif email:
        user = User.get_user_by_email(email)
    if not user and abort:
        api.abort(HTTPStatus.BAD_REQUEST, 'User not found')
    return user


@api.route('/user/register')
class UserRegisterApi(Resource):
    @api.doc('register_user')
    @api.expect(UserDto.user_create_in, validate=True)
    @api.response(201, 'User created', UserDto.user_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    def post(self):
        data = api.payload

        if data.get('email'):
            if not is_valid_email(data['email']):
                api.abort(HTTPStatus.BAD_REQUEST, 'Invalid email')
        if not is_valid_password(data['password']):
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid password')

        user_phone = data['person'].get('phone')
        user_email = data.get('email')

        method = 'phone' if user_phone else 'email' if user_email else None
        if method is None:
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid parameters: email or phone is required.')

        user = User.get_user_by_email(user_email)
        if user:
            api.abort(HTTPStatus.BAD_REQUEST, 'User already exists')
        user = handle_error(User.create(add_last_change_by_id(data)), api)
        return user


@api.route('/user/login')
class UserLoginApi(Resource):
    @api.doc('login_user')
    @api.expect(AuthDto.user_login_in, validate=True)
    @api.response(201, 'Successfully logged in', AuthDto.login_out)
    @api.response(400, 'Wrong parameters')
    @api.response(403, 'Forbidden operation')
    def post(self):
        data = api.payload
        user = get_user(data.get('phone'), data.get('email'))

        if not verify_password(data['password'], User.get_user_password(user['user_id'])):
            api.abort(HTTPStatus.BAD_REQUEST, 'Wrong username or password')

        access_token = Person.encode_access_token(user['person']['person_id'], user_id=user['user_id'])

        return access_token


@api.route('/user/password')
class UserPasswordChangeApi(Resource):
    @api.doc('change_password_user')
    @api.expect(AuthDto.change_in, validate=True)
    @api.response(201, 'Password reset', AuthDto.login_out)
    @api.response(401, 'Unauthorized')
    def post(self):
        @access_token_required()
        def check_access_token(api_):
            return User.get_user_by_id(request.environ['user_id'])

        @access_token_required(False)
        def check_password_reset_token(api_):
            return User.get_user_by_id(request.environ['user_id'])

        data = api.payload
        request.environ['HTTP_AUTHORIZATION'] = data['access_token']
        if not data['is_reset']:
            user = check_access_token(self)
            if user['is_valid_password']:
                if not data.get('old_password'):
                    api.abort(HTTPStatus.BAD_REQUEST, 'No old password provided')

                if not verify_password(data['old_password'], User.get_user_password(user['user_id'])):
                    api.abort(HTTPStatus.BAD_REQUEST, 'Wrong password')
        else:
            user = check_password_reset_token(self)
        if not is_valid_password(data['password']):
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid new password')

        User.set_password(user['user_id'], data['password'])
        access_token = Person.encode_access_token(user['person']['person_id'], user_id=user['user_id'])

        return access_token


@api.route('/staff/login')
class StaffLoginApi(Resource):
    @api.doc('login_staff')
    @api.expect(AuthDto.staff_login_in, validate=True)
    @api.response(201, 'Successfully logged in', AuthDto.login_out)
    @api.response(400, 'Wrong parameters')
    def post(self):
        data = api.payload

        staff = Staff.get_staff_by_email(data['email'])
        if not staff:
            api.abort(HTTPStatus.BAD_REQUEST, 'Account does not exist')

        if not staff['active']:
            api.abort(HTTPStatus.BAD_REQUEST, 'Account is disabled')

        if not verify_password(data['password'], Staff.get_staff_password(staff['id'])):
            api.abort(HTTPStatus.BAD_REQUEST, 'Wrong password')

        access_token = Person.encode_access_token(staff['person']['person_id'], staff['id'])

        return access_token


@api.route('/refresh')
@api.doc(security='access-token')
class RefreshTokenApi(Resource):
    @api.doc('refresh_token')
    @api.expect(AuthDto.refresh_in, validate=True)
    @api.response(201, 'Password reset', AuthDto.login_out)
    def post(self):
        token = handle_error(Person.decode_access_token(api.payload['refresh_token']), api, HTTPStatus.UNAUTHORIZED)
        if not token['sub']['refresh']:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Refresh token required, not access token')
        access_token = Person.encode_access_token(token['sub']['person_id'], token['sub']['staff_id'],
                                                  token['sub']['user_id'], False)
        return access_token
