from collections import OrderedDict
from flask_restplus import Resource

from http import HTTPStatus

from ..model.entity.criteria import Criteria
from ..util.auth import add_last_change_by_id, access_token_required, role_access_required
from ..util.dto import CriteriaDto
from ..util.functions import handle_error

api = CriteriaDto.api

_item_parser = api.parser()
_item_parser.add_argument('criteria_id', type=int, help='Criteria unique identifier', location='args', required=True)


@api.route('')
@api.doc(security='access-token')
class CriteriaApi(Resource):
    @api.doc('get_criteria')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success', CriteriaDto.criteria_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @api.response(404, 'Not Found')
    @access_token_required()
    @role_access_required(['admin', 'administrator'])
    def get(self):
        args = _item_parser.parse_args()
        criteria_dict = Criteria.get_criteria_by_id(args.get('criteria_id'))
        if criteria_dict is None:
            return api.abort(HTTPStatus.NOT_FOUND, f'Criteria with id {args.get("criteria_id")} was not found')
        return criteria_dict

    @api.doc('create_criteria')
    @api.expect(CriteriaDto.criteria_create_in, validate=True)
    @api.response(200, 'Success', CriteriaDto.criteria_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator'])
    def post(self):
        return handle_error(Criteria.create(add_last_change_by_id(api.payload)), api)

    @api.doc('update_criteria')
    @api.expect(CriteriaDto.criteria_update_in, validate=True)
    @api.response(200, 'Success', CriteriaDto.criteria_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator'])
    def put(self):
        return handle_error(Criteria.update(add_last_change_by_id(api.payload)), api)

    @api.doc('delete_criteria')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success', CriteriaDto.criteria_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator'])
    def delete(self):
        args = _item_parser.parse_args()
        return handle_error(Criteria.delete(args.get('criteria_id')), api, HTTPStatus.NOT_FOUND)


@api.route('/list')
@api.doc(security='access-token')
class CriteriaListApi(Resource):
    @api.doc('criteria_list')
    @api.response(200, 'Success', CriteriaDto.criteria_list)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    def get(self):
        all_criterias = Criteria.get_criterias()
        count = len(all_criterias)
        return OrderedDict([('criterias', all_criterias), ('count', count)])

