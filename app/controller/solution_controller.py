from collections import OrderedDict
from flask_restplus import Resource

from http import HTTPStatus

from ..model.entity.solution import Solution
from ..util.auth import add_last_change_by_id, access_token_required, role_access_required, get_user_from_token
from ..util.dto import SolutionDto
from ..util.functions import handle_error
from ..util import get_items_with_relations

api = SolutionDto.api

_item_parser = api.parser()
_item_parser.add_argument('solution_id', type=int, help='Solution unique identifier', location='args', required=True)


@api.route('')
@api.doc(security='access-token')
class SolutionApi(Resource):
    @api.doc('submit_solution')
    @api.expect(SolutionDto.solution_create_in, validate=True)
    @api.response(200, 'Success', SolutionDto.solution_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    def post(self):
        user = get_user_from_token(api)
        data = api.payload
        data['user_id'] = user['user_id']
        solution = Solution.get_solution_by_user_and_event(user['user_id'], data['event_id'])
        if solution is not None:
            api.abort(HTTPStatus.BAD_REQUEST, f'You can only submit one solution for each event')
        solution = handle_error(Solution.create(add_last_change_by_id(data)), api)
        return solution

    @api.doc('get_solution')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success', SolutionDto.solution_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    def get(self):
        args = _item_parser.parse_args()
        solution = Solution.get_solution_by_id(args.get('solution_id'))
        if solution is None:
            api.abort(HTTPStatus.NOT_FOUND, f'Solution with id {args.get("solution_id")} was not found')
        solution = get_items_with_relations([solution], Solution, None, ['marks'])
        return solution

    @api.doc('update_solution')
    @api.expect(SolutionDto.solution_update_in)
    @api.response(200, 'Success', SolutionDto.solution_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    def put(self):
        return handle_error(Solution.update(add_last_change_by_id(api.payload)), api)
