from collections import OrderedDict
from flask_restplus import Resource

from http import HTTPStatus

from ..model import Solution
from ..model.entity.criteria import Criteria
from ..model.entity.pairing_mark import PairingMark
from ..util.auth import add_last_change_by_id, access_token_required, role_access_required, get_staff_from_token
from ..util.dto import PairingMarkDto
from ..util.functions import handle_error

api = PairingMarkDto.api

_item_parser = api.parser()
_item_parser.add_argument('event_id', type=int, help='The event identifier.', location='args', required=True)


@api.route('')
@api.doc(security='access-token')
class MarkApi(Resource):
    @api.doc('create_mark')
    @api.expect(PairingMarkDto.pairing_mark_create_in, validate=True)
    @api.response(200, 'Success', PairingMarkDto.pairing_mark_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def post(self):
        staff = get_staff_from_token(api)
        data = api.payload
        criteria = Criteria.get_criteria_by_id(data['criteria_id'])
        if criteria is None:
            api.abort(HTTPStatus.BAD_REQUEST, f'Criteria with id {data["criteria_id"]} was not found')
        if data['score'] > 2 or data['score'] < 0:
            api.abort(HTTPStatus.BAD_REQUEST, 'Not acceptable score')
        data['staff_id'] = staff['id']
        return handle_error(PairingMark.create(add_last_change_by_id(data)), api)

    @api.doc('update_mark')
    @api.expect(PairingMarkDto.pairing_mark_update_in, validate=True)
    @api.response(200, 'Success', PairingMarkDto.pairing_update_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def put(self):
        data = api.payload
        staff = get_staff_from_token(api)
        data['staff_id'] = staff['id']
        if data['score'] > 2 or data['score'] < 0:
            api.abort(HTTPStatus.BAD_REQUEST, 'Not acceptable score')
        mark, mark_list = PairingMark.update_tree(add_last_change_by_id(data))
        return OrderedDict([('updated_mark', mark), ('automatically_updated_marks', mark_list)])


@api.route('/new_pair')
@api.doc(security='access-token')
class NewPairMarkApi(Resource):
    @api.doc('start marking')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success')
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def get(self):
        args = _item_parser.parse_args()
        staff = get_staff_from_token(api)
        return handle_error(PairingMark.get_pair_for_marking(staff['id'], args['event_id']))


@api.route('/start')
@api.doc(security='access-token')
class StartMarkApi(Resource):
    @api.doc('start marking')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success')
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def post(self):
        args = _item_parser.parse_args()
        staff = get_staff_from_token(api)
        handle_error(Solution.create_all_pairs(args['event_id'], staff['id']))
        return 'Success'
