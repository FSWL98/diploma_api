from collections import OrderedDict
from http import HTTPStatus

from flask_restx import Resource

from ..model import User
from ..model.entity.role import Role
from ..model.entity.staff import Staff
from ..model.relation.user_staff import UserStaff
from ..util import all_in, get_items_related_to_page, get_items_with_relations
from ..util.auth import add_last_change_by_id, access_token_required, get_staff_from_token, is_valid_password, \
    role_access_required
from ..util.dto import StaffDto, UserDto
from ..util.functions import handle_error
from ..util.mail import is_valid_email

api = StaffDto.api

_list_parser = api.parser()
_list_parser.add_argument('page_id', type=int, help='The page identifier.', location='args', default=0)
_list_parser.add_argument('page_size', type=int, help='The page size. -1 means all.', location='args',
                          default=-1)
_list_parser.add_argument('query', type=str, help='The search query', location='args', store_missing=False)
_list_parser.add_argument('roles', type=int, help='The roles ids', location='args', action='split',
                          store_missing=False)

_staff_filters = {
    'roles': lambda role_ids: lambda staff: all_in(role_ids, [r['id'] for r in staff['roles']])
}

_item_parser = api.parser()
_item_parser.add_argument('id', type=int, help='The staff identifier.', location='args', required=True)


@api.route('')
@api.doc(security='access-token')
class StaffApi(Resource):
    @api.doc('get_staff')
    @api.response(200, 'Success', StaffDto.staff_list)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['admin', 'administrator'])
    def get(self):
        staff = Staff.get_items()
        count = len(staff)
        return OrderedDict([('staff', staff), ('count', count)])

    @api.doc('create_staff')
    @api.expect(StaffDto.staff_create_in)
    @api.response(201, 'Staff created', StaffDto.staff_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant'])
    def post(self):
        data = api.payload
        if not (data.get('email') and data.get('password')):
            api.abort(HTTPStatus.BAD_REQUEST, 'Email and password should be specified!')

        if not is_valid_email(data['email']):
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid email')
        data['is_valid_mail'] = True

        if not is_valid_password(data['password']):
            api.abort(HTTPStatus.BAD_REQUEST, 'Invalid password')
        staff = handle_error(Staff.create(add_last_change_by_id(data)), api)

        return staff

    @api.doc('edit_staff')
    @api.expect(StaffDto.staff_update_in, validate=True)
    @api.response(201, 'Staff updated', StaffDto.staff_put_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant'])
    def put(self):
        data = api.payload

        if data.get('email'):
            if not is_valid_email(data['email']):
                api.abort(HTTPStatus.BAD_REQUEST, 'Invalid email')
            data['is_valid_mail'] = True

        if data.get('password'):
            if not is_valid_password(data['password']):
                api.abort(HTTPStatus.BAD_REQUEST, 'Invalid password')
            handle_error(Staff.set_password(data['id'], data['password']), api)
        return handle_error(Staff.update(add_last_change_by_id(data)), api)

    @api.doc('delete_staff')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Staff deleted', StaffDto.staff_out)
    @api.response(400, 'Wrong params')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Staff not found')
    @access_token_required()
    @role_access_required('administrator')
    def delete(self):
        args = _item_parser.parse_args()
        return handle_error(Staff.delete(args['id']), api, HTTPStatus.NOT_FOUND)


@api.route('/me')
@api.doc(security='access-token')
class StaffMeApi(Resource):
    @api.doc('get_me_staff')
    @api.response(200, 'Success', StaffDto.staff_out)
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Only for staff')
    @access_token_required()
    def get(self):
        staff = get_staff_from_token(api)
        return staff


@api.route('/user')
@api.doc(security='access-token')
class StaffApiUser(Resource):
    @api.doc('get_staff_users')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success', UserDto.user_list)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    @role_access_required(['administrator', 'assistant'])
    def get(self):
        args = _item_parser.parse_args()
        user_ids = UserStaff.get_relation_ids_by_staff(args['id'])
        staff_users = [User.get_user_by_id(user_id) for user_id in user_ids]
        return OrderedDict({"users": staff_users, "count": len(staff_users)})
