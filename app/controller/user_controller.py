from collections import OrderedDict
from http import HTTPStatus

from flask import request
from flask_restx import Resource

from ..model.entity.staff import Staff
from ..model.entity.user import User
from ..model.relation.user_staff import UserStaff
from ..util import get_items_related_to_page, \
    get_items_with_relations, get_bot_start_link
from ..util.auth import add_last_change_by_id, access_token_required, check_user_staff_access, \
    get_user_from_token, is_doctor, is_valid_password, role_access_required
from ..util.dto import UserDto
from ..util.functions import handle_error
from ..util.mail import is_valid_email

api = UserDto.api


_list_parser = api.parser()
_list_parser.add_argument('page_id', type=int, help='The page identifier.', location='args', default=0)
_list_parser.add_argument('page_size', type=int, help='The page size. -1 means all.', location='args',
                          default=-1)
_list_parser.add_argument('query', type=str, help='The search query', location='args', store_missing=False)

_item_parser = api.parser()
_item_parser.add_argument('user_id', type=int, help='The user identifier.', location='args', required=True)

_relation_parser = api.parser()
_relation_parser.add_argument('user_id', type=str, help='The user identifier.', location='args', required=True)
_relation_parser.add_argument('staff_id', type=str, help='The staff identifier.', location='args', required=True)

_delete_parser = api.parser()
_delete_parser.add_argument('user_id', type=str, help='The user identifier.', location='args', required=True)


def sort_user_func(user):
    return has_unlabelled_docs(user), \
           user['documents'][0]['create_date'] if len(user['documents']) else user['create_date']


def has_unlabelled_docs(user):
    return not user['documents'][0]['is_labeled'] if len(user['documents']) else False


def filter_users_by_doctor(users):
    return [user for user in users if check_user_staff_access(api, user['user_id'], abort=False)]


@api.route('')
@api.doc(security='access-token')
class UserApi(Resource):
    @api.doc('get_users')
    @api.expect(_list_parser, validate=True)
    @api.response(200, 'Success', UserDto.user_list)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant', 'doctor'])
    def get(self):
        args = _list_parser.parse_args()

        if args.get('query'):
            items, total = User.search(args['query'])
            if is_doctor(request.environ['staff_id']):
                items = filter_users_by_doctor(items)
            count = len(items)
            users = get_items_related_to_page(args['page_id'], args['page_size'], items)
        else:
            if is_doctor(request.environ['staff_id']):
                items = [User.get_user_by_id(user_id) for user_id in
                         UserStaff.get_relation_ids_by_staff(request.environ['staff_id'])]
                count = len(items)
                users = get_items_related_to_page(args['page_id'], args['page_size'], items)
            else:
                users, count = User.get_items(args['page_id'], args['page_size'])

        users = sorted(users, key=lambda user: sort_user_func(user), reverse=True)
        return OrderedDict([('users', users), ('count', count)])

    @api.doc('create_user')
    @api.expect(UserDto.user_create_in, validate=True)
    @api.response(201, 'User created', UserDto.user_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant'])
    def post(self):
        data = api.payload

        if data.get('email') and not is_valid_email(data['email']):
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid email')

        if not is_valid_password(data['password']):
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid password')

        return handle_error(User.create(add_last_change_by_id(data)), api)

    @api.doc('edit_user')
    @api.expect(UserDto.user_update_in, validate=True)
    @api.response(201, 'User updated', UserDto.user_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant'])
    def put(self):
        data = api.payload
        if data.get('password'):
            if not is_valid_password(data['password']):
                api.abort(HTTPStatus.BAD_REQUEST, 'Invalid password')
            handle_error(User.set_password(data['user_id'], data['password']), api)

        return handle_error(User.update(add_last_change_by_id(data)), api)

    @api.doc('delete_user')
    @api.expect(_delete_parser)
    @api.response(200, 'User deleted', UserDto.user_out)
    @api.response(400, 'Wrong params')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'User not found')
    @access_token_required()
    @role_access_required(['administrator'])
    def delete(self):
        args = _delete_parser.parse_args()
        return handle_error(User.delete(args['user_id']), api, HTTPStatus.NOT_FOUND)


@api.route('/me')
@api.doc(security='access-token')
class UserApi(Resource):
    @api.doc('get_me')
    @api.response(200, 'Success')
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @access_token_required()
    def get(self):
        user = get_user_from_token(api)
        return user

    @api.doc('edit_me')
    @api.expect(UserDto.user_me_update_in, validate=True)
    @api.response(201, 'User updated')
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @access_token_required()
    def put(self):
        data = api.payload

        user = get_user_from_token(api)
        data['person']['person_id'] = user['person']['person_id']
        data['user_id'] = user['user_id']

        if 'email' in data:
            del data['email']

        user = handle_error(User.update(add_last_change_by_id(data)), api)
        return user


@api.route('/info')
@api.doc(security='access-token')
class UserInfoApi(Resource):
    @api.doc('get_user_info')
    @api.expect(_item_parser)
    @api.response(200, 'Success', UserDto.user_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant', 'doctor'])
    def get(self):
        args = _item_parser.parse_args()
        staff = Staff.get_staff_instance_by_id(request.environ['staff_id'])
        if staff.has_role('doctor') and not UserStaff.get_relation(args['user_id'], request.environ['staff_id']):
            api.abort(HTTPStatus.FORBIDDEN, "This user is not related to the staff person!")
        else:
            user = User.get_user_by_id(args['user_id'])
            if not user:
                api.abort(HTTPStatus.NOT_FOUND, 'User not found')

        return user
