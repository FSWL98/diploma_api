from collections import OrderedDict
from flask_restplus import Resource

from http import HTTPStatus

from ..model.entity.criteria import Criteria
from ..model.entity.mark import Mark
from ..util.auth import add_last_change_by_id, access_token_required, role_access_required, get_staff_from_token
from ..util.dto import MarkDto
from ..util.functions import handle_error

api = MarkDto.api


@api.route('')
@api.doc(security='access-token')
class MarkApi(Resource):
    @api.doc('create_mark')
    @api.expect(MarkDto.mark_create_in, validate=True)
    @api.response(200, 'Success', MarkDto.mark_out)
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
        if data['score'] > criteria['maximum'] or data['score'] < criteria['minimum']:
            api.abort(HTTPStatus.BAD_REQUEST, 'Недопустимая оценка')
        data['staff_id'] = staff['id']
        return handle_error(Mark.create(add_last_change_by_id(data)), api)

    @api.doc('edit_mark')
    @api.expect(MarkDto.mark_update_in, validate=True)
    @api.response(200, 'Success', MarkDto.mark_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def put(self):
        data = api.payload
        criteria = Criteria.get_criteria_by_id(data['criteria_id'])
        if criteria is None:
            api.abort(HTTPStatus.BAD_REQUEST, f'Criteria with id {data["criteria_id"]} was not found')
        if data['score'] > criteria['maximum'] or data['score'] < criteria['minimum']:
            api.abort(HTTPStatus.BAD_REQUEST, 'Недопустимая оценка')
        return handle_error(Mark.update(add_last_change_by_id(api.payload)), api)
