from collections import OrderedDict
from flask_restplus import Resource

from http import HTTPStatus

from ..model.entity.event import Event
from ..model.relation.user_event import UserEvent
from ..model.entity.solution import Solution
from ..util.auth import add_last_change_by_id, access_token_required, role_access_required, get_user_from_token
from ..util.dto import EventDto
from ..util.functions import handle_error

api = EventDto.api

_item_parser = api.parser()
_item_parser.add_argument('event_id', type=int, help='The event identifier.', location='args', required=True)

_not_required_item_parser = api.parser()
_not_required_item_parser.add_argument('event_id', type=int, help='The event identifier', location='args', required=False)


@api.route('/')
@api.doc(security='access-token')
class EventListApi(Resource):
    @api.doc('list_event')
    @api.response(200, 'Success', EventDto.event_list)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @access_token_required()
    def get(self):
        all_events = Event.get_events()
        count = len(all_events)
        return OrderedDict([('events', all_events), ('count', count)])

    @api.doc('create_event')
    @api.expect(EventDto.event_in, validate=True)
    @api.response(200, 'Success', EventDto.event_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def post(self):
        return handle_error(Event.create(add_last_change_by_id(api.payload)), api)

    @api.doc('update_event')
    @api.expect(EventDto.event_in_update, validate=True)
    @api.response(200, 'Success', EventDto.event_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator', 'staff'])
    def put(self):
        return handle_error(Event.update(add_last_change_by_id(api.payload)), api)

    @api.doc('delete_event')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success', EventDto.event_out)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    @role_access_required(['admin', 'administrator'])
    def delete(self):
        args = _item_parser.parse_args()
        return handle_error(Event.delete(args['event_id']), api, HTTPStatus.NOT_FOUND)


@api.route('/register')
@api.doc(security='access-token')
class EventRegisterApi(Resource):
    @api.doc('register_user_for_event')
    @api.expect(_item_parser, validate=True)
    @api.response(200, 'Success')
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    def post(self):
        args = _item_parser.parse_args()
        user = get_user_from_token(api)
        return handle_error(UserEvent.create_by_id(user['user_id'], args.get('event_id')))


@api.route('/user')
@api.doc(security='access-token')
class EventUserApi(Resource):
    @api.doc('get_user_events')
    @api.expect(_not_required_item_parser)
    @api.response(200, 'Success', EventDto.event_list)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @access_token_required()
    def get(self):
        args = _not_required_item_parser.parse_args()
        user = get_user_from_token(api)
        if user is None:
            api.abort(HTTPStatus.BAD_REQUEST)
        user_event_list = [item['event_id'] for item in UserEvent.get_relations_by_user(user['user_id'])]
        if args.get('event_id'):
            events = [Event.get_event_by_id(args.get('event_id'))]
        else:
            events = Event.get_events()

        for event in events:
            event['is_registered'] = event['event_id'] in user_event_list
            solution = Solution.get_solution_by_user_and_event(user['user_id'], event['event_id'])
            event['solution'] = solution

        count = len(events)
        return OrderedDict([('events', events), ('count', count)])
