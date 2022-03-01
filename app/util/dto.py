from datetime import datetime, time
from flask_restx import fields, Namespace


class TimeHM(fields.DateTime):
    __schema_example__ = datetime.utcnow().time().strftime('%H:%M')
    __schema_format__ = 'time-hm'

    def __init__(self, **kwargs):
        kwargs.pop('dt_format', None)
        super(TimeHM, self).__init__(dt_format='iso8601', **kwargs)

    def parse(self, value):
        if value is None:
            return None
        elif isinstance(value, fields.string_types):
            return fields.date_from_iso8601(value).time()
        elif isinstance(value, datetime):
            return value.time()
        elif isinstance(value, time):
            return value
        else:
            raise ValueError('Unsupported Time format')


class NullableString(fields.String):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'


class NullableInteger(fields.Integer):
    __schema_type__ = ['integer', 'null']
    __schema_example__ = 0


class NullableBoolean(fields.Boolean):
    __schema_type__ = ['boolean', 'null']
    __schema_example__ = 0


fields.Date.__schema_example__ = datetime.utcnow().date().isoformat()

GENDERS = ['male', 'female']


class DefaultDto:
    api = Namespace('default', description='Default operations')
    version = api.model('version', {
        'version': fields.String(required=True, description='The number of version')
    })


class AuthDto:
    api = Namespace('auth', description='Auth operations')
    user_login_in = api.model('user_login_in', {
        'phone': fields.String(description='User phone'),
        'email': fields.String(description='User email'),
        'password': fields.String(description='User password')
    })

    user_confirm_send = api.model('user_confirm_send', {
        'user_id': fields.Integer(description='User identifier'),
        'phone': fields.String(description='User phone'),
        'email': fields.String(description='User email'),
    })

    reset_in = api.model('reset_in', {
        'phone': fields.String(description='User phone'),
        'email': fields.String(description='User email')
    })

    change_in = api.model('change_in', {
        'password': fields.String(required=True, description=' New password'),
        'is_reset': fields.Boolean(required=True, description='Flag if password is being reset or changed'),
        'access_token': fields.String(required=True, description='The access token.'),
        'old_password': fields.String(description='Old password')
    })

    user_confirm = api.model('user_confirm', {
        'user_id': fields.Integer(required=True, description='User identifier'),
        'code': fields.String(required=True, description='Confirmation code')
    })

    confirm_reset_in = api.model('confirm_reset_in', {
        'phone': fields.String(description='User phone'),
        'email': fields.String(description='User email'),
        'code': fields.String(required=True, description='Confirmation code')
    })

    staff_login_in = api.model('staff_login_in', {
        'email': fields.String(required=True, description='Staff email'),
        'password': fields.String(required=True, description='Staff password')
    })

    login_out = api.model('login_out', {
        'status': fields.String(required=True, description='Request status'),
        'message': fields.String(required=True, description='Status message'),
        'access_token': fields.String(description='JWT access token')
    })

    refresh_in = api.model('refresh_in', {
        'refresh_token': fields.String(required=True, description='Refresh token')
    })


class ReleaseDto:
    api = Namespace('release', description='Release operations')


class PersonDto:
    api = Namespace('person', description='Person operations')

    person = api.model('person', {
        'phone': NullableString(description='The person phone number'),
        'chat_id': NullableInteger(description='The person telegram chat identifier'),
        'tg_username': NullableString(description='The person telegram username'),
        'name': NullableString(description='The person name'),
        'surname': NullableString(description='The person surname'),
        'patronymic': NullableString(description='The person patronymic'),
        'gender': NullableString(description='The person gender'),
        'avatar': NullableString(description='Person avatar'),
        'is_confirmed': fields.Boolean(description='Flag if user can log in'),
        'notification_method': NullableString(
            description='User preferred message channel. Three are available: telegram, phone and email')
    })


class StaffDto:
    api = Namespace('staff', description='Staff operations')

    person = api.model('person', {
        'phone': NullableString(description='The person phone number'),
        'chat_id': NullableInteger(description='The person telegram chat identifier'),
        'tg_username': NullableString(description='The person telegram username'),
        'name': NullableString(required=True, description='The person name'),
        'surname': NullableString(required=True, description='The person surname'),
        'patronymic': NullableString(description='The person patronymic'),
        'gender': NullableString(description='The person gender'),
        'avatar': NullableString(description='Person avatar'),
        'is_confirmed': NullableBoolean(description='Flag if user can log in'),
        'notification_method': NullableString(
            description='User preferred message channel. Three are available: telegram, phone and email')
    })

    role_out = api.model('role_out', {
        'id': fields.Integer(required=True, description='The role identifier'),
        'name': fields.String(required=True, description='The role name'),
        'description': fields.String(required=True, description='The role description'),
        'level': fields.Integer(required=True, description='The role level'),
    })

    staff_create_in = api.model('staff_create_in', {
        'email': fields.String(reqired=True, description='The staff email'),
        'password': fields.String(required=True, description='The staff password'),
        'bio': NullableString(description='The staff information'),
        'active': fields.Boolean(required=True, description='Is staff active'),
        'person': fields.Nested(person, required=True, description='Staff person information'),
        'roles': fields.List(fields.String, description='Staff roles'),
        'external': fields.Boolean(description='Is external staff'),
        'labels': fields.List(fields.Integer, description='The list of labels ids'),
        'science_degrees': fields.List(fields.Integer, description='The list of science_degrees ids'),
        'specialities': fields.List(fields.Integer, description='The list of specialities ids'),
        'main_speciality_id': fields.Integer(description='The main speciality identifier'),
        'staff_categories': fields.List(fields.Integer, description='The list of staff_categories ids'),
        'partners': fields.List(fields.Integer, description='Partner identifier'),
        'clinics': fields.List(fields.Integer, description='The list of clinic ids'),
    })

    staff_out = api.model('staff_out', {
        'id': fields.Integer(required=True, description='Staff identifier'),
        'email': fields.String(required=True, description='Staff email'),
        'bio': fields.String(required=True, description='Staff information'),
        'active': fields.String(required=True, description='Is staff active'),
        'person': fields.Nested(person, required=True, description='Staff person information'),
        'roles': fields.List(fields.Nested(role_out), required=True, description='Staff roles'),
        'create_date': fields.DateTime(required=True, description='Staff creation date'),
        'update_date': fields.DateTime(required=True, description='Staff edit date'),
        'labels': fields.List(fields.Integer, required=True, description='The list of labels ids'),
        'science_degrees': fields.List(fields.Integer, required=True, description='The list of science_degrees ids'),
        'specialities': fields.List(fields.Integer, required=True, description='The list of specialities ids'),
        'main_speciality_id': fields.Integer(required=True, description='The main speciality identifier'),
        'staff_categories': fields.List(fields.Integer, required=True, description='The list of staff_categories ids'),
        'partners': fields.List(fields.Integer, description='Partner identifier'),
        'clinics': fields.List(fields.Integer, description='The list of clinic ids'),
    })

    staff_list = api.model('staff_list', {
        'staff': fields.List(fields.Nested(staff_out), required=True, description='The list of staff'),
        'count': fields.Integer(required=True, description='The count of staff'),
        'roles': fields.List(fields.Nested(role_out), required=True, description='The list of roles'),
    })

    staff_update_in = api.model('staff_update_in', {
        'id': fields.Integer(required=True, description='The staff identifier'),
        'email': fields.String(description='The staff email'),
        'password': fields.String(description='The staff password'),
        'bio': NullableString(description='The staff information'),
        'active': fields.Boolean(description='Is staff active'),
        'person': fields.Nested(person, required=True, description='Staff person information'),
        'roles': fields.List(fields.String, description='Staff roles'),
        'external': fields.Boolean(description='Is external staff'),
        'labels': fields.List(fields.Integer, description='The list of labels ids'),
        'science_degrees': fields.List(fields.Integer, description='The list of science_degrees ids'),
        'specialities': fields.List(fields.Integer, description='The list of specialities ids'),
        'main_speciality_id': NullableInteger(description='The main speciality identifier'),
        'staff_categories': fields.List(fields.Integer, description='The list of staff_categories ids'),
        'partners': fields.List(fields.Integer, description='Partner identifier'),
        'clinics': fields.List(fields.Integer, description='The list of clinic ids'),
    })

    staff_put_out = api.clone('staff_put_out', staff_update_in)

    staff_bot_out = api.model('staff_bot_out', {
        'id': fields.Integer(required=True, description='Staff identifier'),
        'person': fields.Nested(person, required=True, description='Staff person information'),
        'alias': fields.String(required=True, description='Staff alias'),
        'roles': fields.List(fields.Nested(role_out), required=True, description='Staff roles'),
        'bio': fields.String(required=True, description='Staff information'),
        'timezone': fields.Integer(required=True, description='Staff timezone'),
        'email': fields.String(required=True, description='Staff email'),
        'active': fields.String(required=True, description='Is staff active'),
        'create_date': fields.DateTime(required=True, description='Staff creation date'),
        'update_date': fields.DateTime(required=True, description='Staff edit date'),
    })

    staff_bot_update_in = api.model('staff_bot_update_in', {
        'id': fields.Integer(required=True, description='The Staff identifier'),
        'person': fields.Nested(person, description='Staff person'),
        'timezone': fields.Integer(description='Staff timezone'),
        'flags': fields.String(description='Staff flags')
    })


class EventDto:
    api = Namespace('event', description='event operations')

    event_id = api.model('event_id', {
        'event_id': fields.Integer(required=True, description='Event unique identifier')
    })

    event_in = api.model('event_in', {
        'name': fields.String(required=True, description='Event name'),
        'date_start': fields.DateTime(required=True, description='Event start date'),
        'date_end': fields.DateTime(required=True, description='Event end date'),
        'evaluation_method': fields.String(description='Method of event evaluation (default to "simple")')
    })

    event_in_update = api.model('event_in_update', {
        'event_id': fields.Integer(required=True, description='Event unique identifier'),
        'name': fields.String(required=True, description='Event name'),
        'date_start': fields.DateTime(required=True, description='Event start date'),
        'date_end': fields.DateTime(required=True, description='Event end date'),
        'evaluation_method': fields.String(description='Method of event evaluation (default to "simple")')
    })

    event_out = api.model('event_out', {
        'event_id': fields.Integer(required=True, description='Event identifier'),
        'name': fields.String(required=True, description='Event name'),
        'date_start': fields.DateTime(required=True, description='Event start date'),
        'date_end': fields.DateTime(required=True, description='Event end date'),
        'evaluation_method': fields.String(required=True, description='Method of event evaluation (default to "simple")'),
        'create_date': fields.DateTime(required=True, description='Event create date'),
        'update_date': fields.DateTime(required=True, description='Last update date')
    })

    event_list = api.model('event_list', {
        'events': fields.List(fields.Nested(event_out), required=True, description='List of events'),
        'count': fields.Integer(required=True, description='Full amount of events in DB')
    })


class UserDto:
    api = Namespace('user', description='user operations')

    person = api.model('person', {
        'phone': NullableString(description='The person phone number'),
        'chat_id': NullableInteger(description='The person telegram chat identifier'),
        'tg_username': NullableString(description='The person telegram username'),
        'name': NullableString(description='The person name'),
        'surname': NullableString(description='The person surname'),
        'patronymic': NullableString(description='The person patronymic'),
        'gender': NullableString(description='The person gender'),
        'avatar': NullableString(description='Person avatar'),
        'is_confirmed': NullableBoolean(description='Flag if user can log in'),
        'notification_method': NullableString(
            description='User preferred message channel. Three are available: telegram, phone and email'),
        'can_receive_tg_notifications': fields.Boolean(description='Tg notification flag'),
        'can_receive_tg_screening': fields.Boolean(description='Tg screening flag'),
        'can_receive_tg_news': fields.Boolean(description='Tg news flag')
    })

    user_create_in = api.model('user_create_in', {
        'password': fields.String(description='User password'),
        'person': fields.Nested(person, description='User person information'),
        'email': NullableString(description='The user email'),
        'birthdate': fields.Date(description='User birthdate'),
        'timezone': fields.Integer(description='User timezone'),
    })

    user_bot_create_in = api.model('user_bot_create_in', {
        'name': fields.String(required=True, description='User person name'),
        'surname': fields.String(required=True, description='User person surname'),
        'patronymic': fields.String(description='User person patronymic'),
        'gender': fields.String(required=True, description='User person gander'),
        'email': fields.String(description='The user email'),
        'birthdate': fields.Date(description='User birthdate'),
        'timezone': fields.Integer(description='User timezone'),
    })

    user_out = api.model('user_out', {
        'user_id': fields.Integer(required=True, description='User identifier'),
        'person': fields.Nested(person, required=True, description='User person information'),
        'email': fields.String(required=True, description='User email'),
        'birthdate': fields.Date(required=True, description='User birthdate'),
        'timezone': fields.Integer(required=True, description='User timezone'),
        'occupation': fields.String(required=True, description='User occupation'),
        'notification_method': fields.String(required=True,
                                             description='User preferred message channel. Three are available: telegram, phone and email'),
        'alias': fields.String(required=True, description='User alias'),
        'is_bot_active': fields.Boolean(required=True, description='Whether user blocked the bot'),
        'flags': fields.String(required=True, description='User flags'),
        'create_date': fields.DateTime(required=True, description='User creation date'),
        'update_date': fields.DateTime(required=True, description='User edit date'),
        'last_change_by_id': fields.Integer(required=True, description='Person identifier who changed the last time'),
    })


    user_list = api.model('user_list', {
        'users': fields.List(fields.Nested(user_out), required=True, description='The list of user'),
        'count': fields.Integer(required=True, description='The count of user')
    })

    user_update_in = api.model('user_update_in', {
        'user_id': fields.Integer(required=True, description='The user identifier'),
        'email': NullableString(description='The user email'),
        'password': fields.String(description='User password'),
        'person': fields.Nested(person, required=True, description='User person information'),
        'is_bot_active': fields.Boolean(description='Whether user blocked the bot'),
        'birthdate': fields.Date(description='User birthdate'),
        'timezone': NullableInteger(description='User timezone'),
        'occupation': NullableString(description='User occupation'),
    })

    user_me_update_in = api.model('user_me_update_in', {
        'person': fields.Nested(person, required=True, description='User person information'),
        'is_bot_active': fields.Boolean(description='Whether user blocked the bot'),
        'birthdate': fields.Date(description='User birthdate'),
        'timezone': NullableInteger(description='User timezone'),
        'occupation': NullableString(description='User occupation'),
    })

    user_me_update_contact = api.model('user_me_update_contact', {
        'email': fields.String(description='The user email'),
        'phone': fields.String(description='User phone'),
        'code': fields.String(required=True, description='Confirmation code')
    })

    user_bot_attach_in = api.model('user_bot_attach_in', {
        'chat_id': fields.Integer(description='Telegram chat unique identifier', required=True),
        'code': fields.String(description='Attendee bot code', required=True),
        'tg_username': fields.String(description='Attendee telegram username')
    })

    user_bot_update_in = api.model('user_bot_update_in', {
        'user_id': fields.Integer(required=True, description='The user identifier'),
        'name': fields.String(description='The user name'),
        'surname': fields.String(description='The user surname'),
        'patronymic': fields.String(description='The person patronymic'),
        'gender': fields.String(description='The person gender'),
        'birthdate': fields.Date(description='User birthdate'),
        'timezone': fields.Integer(description='User timezone'),
        'occupation': fields.String(description='User occupation'),
        'flags': fields.String(description='User flags'),
        'person': fields.Nested(person, description='User person information'),
    })

    user_state = api.model('user_state_in', {
        'chat_id': fields.Integer(required=True, description='The chat identifier'),
        'bot_id': fields.Integer(required=True, description='The bot identifier'),
        'state_config': fields.String(required=True, description='The state config (Dumped json)'),
    })

    user_state_edit_array = api.model('user_state_edit_in', {
        'chat_id': fields.Integer(required=True, description='The chat identifier'),
        'bot_id': fields.Integer(required=True, description='The bot identifier'),
        'add_ids': fields.List(fields.Integer, default=[], description='The identifiers to add to array'),
        'del_ids': fields.List(fields.Integer, default=[], description='The identifiers to delete from array'),
        'array_name': fields.String(required=True, description='The array to edit field name')
    })

    message_text = api.model('text', {
        'title': fields.String(required=True, description='Message title'),
        'body': fields.String(required=True, description='Message text in jinja format.')
    })

    user_message_send = api.model('user_message_send', {
        'message_template_name': fields.String(description='Message template unique name'),
        'text': fields.Nested(message_text, description='Message text, if template does not fit.'),
        'person_id': fields.Integer(required=True, description='Addressee\'s person identifier'),
        'demanded_notification_method': fields.String(description='Messaging channel. Three are available: telegram, '
                                                                  'phone and email'),
        'sending_address': fields.String(description='Messaging custom address. If method is phone, this field is phone, '
                                                     'and so on.'),
    })


class CriteriaDto:
    api = Namespace('criteria', description='criteria operations')

    criteria_create_in = api.model('criteria_create_in', {
        'name': fields.String(required=True, description='Criteria name'),
        'description': NullableString(description='Criteria description'),
        'minimum': fields.Integer(required=True, description='Criteria minimum score'),
        'maximum': fields.Integer(required=True, description='Criteria maximum score')
    })

    criteria_update_in = api.model('criteria_update_in', {
        'criteria_id': fields.Integer(required=True, description='Criteria unique identifier'),
        'name': fields.String(required=True, description='Criteria name'),
        'description': NullableString(description='Criteria description'),
        'minimum': fields.Integer(required=True, description='Criteria minimum score'),
        'maximum': fields.Integer(required=True, description='Criteria maximum score')
    })

    criteria_out = api.model('criteria_out', {
        'criteria_id': fields.Integer(required=True, description='Criteria unique identifier'),
        'name': fields.String(required=True, description='Criteria name'),
        'description': NullableString(description='Criteria description'),
        'minimum': fields.Integer(required=True, description='Criteria minimum score'),
        'maximum': fields.Integer(required=True, description='Criteria maximum score'),
        'create_date': fields.DateTime(required=True, description='Event create date'),
        'update_date': fields.DateTime(required=True, description='Last update date'),
        'last_change_by_id': fields.Integer(required=True, description='Person identifier who changed the last time')
    })

    criteria_list = api.model('criteria_list', {
        'criterias': fields.List(fields.Nested(criteria_out), description='List of criterias'),
        'count': fields.Integer(description='Amount of criterias')
    })


class MarkDto:
    api = Namespace('mark', description='Mark operations')

    mark_create_in = api.model('mark_create_in', {
        'solution_id': fields.Integer(required=True, description='Marked solution unique identifier'),
        'criteria_id': fields.Integer(required=True, description='Marked criteria unique identifier'),
        'score': fields.Integer(required=True, description='Score of the solution in this criteria'),
        'comment': NullableString(description='Comment on the score')
    })

    mark_update_in = api.model('mark_update_in', {
        'mark_id': fields.Integer(required=True, description='Mark unique identifier'),
        'score': fields.Integer(required=True, description='Score of the solution in this criteria'),
        'comment': NullableString(description='Comment on the score')
    })

    mark_out = api.model('mark_out', {
        'mark_id': fields.Integer(required=True, description='Mark unique identifier'),
        'solution_id': fields.Integer(required=True, description='Marked solution unique identifier'),
        'criteria_id': fields.Integer(required=True, description='Marked criteria unique identifier'),
        'staff_id': fields.Integer(required=True, description='Staff unique identifier'),
        'score': fields.Integer(required=True, description='Score of the solution in this criteria'),
        'comment': NullableString(description='Comment on the score'),
        'create_date': fields.DateTime(required=True, description='Event create date'),
        'update_date': fields.DateTime(required=True, description='Last update date'),
        'last_change_by_id': fields.Integer(required=True, description='Person identifier who changed the last time')
    })


class SolutionDto:
    api = Namespace('solution', description='Solution operations')

    solution_create_in = api.model('solution_create_in', {
        'event_id': fields.Integer(required=True, description='Event unique identifier (for which solution is)'),
        'url': fields.String(required=True, description='Link to solution'),
        'description': NullableString(description='Solution description')
    })

    solution_update_in = api.model('solution_update_in', {
        'solution_id': fields.Integer(required=True, description='Solution unique identifier'),
        'url': fields.String(required=True, description='Link to solution'),
        'description': NullableString(description='Solution description')
    })

    solution_out = api.model('solution_out', {
        'solution_id': fields.Integer(required=True, description='Solution unique identifier'),
        'user_id': fields.Integer(required=True, description='User unique identifier (whose solution is)'),
        'event_id': fields.Integer(required=True, description='Event unique identifier (for which solution is)'),
        'url': fields.String(required=True, description='Link to solution'),
        'description': NullableString(description='Solution description'),
        'marks': fields.List(fields.Nested(MarkDto.mark_out), description='List of marks for solution'),
        'create_date': fields.DateTime(required=True, description='Event create date'),
        'update_date': fields.DateTime(required=True, description='Last update date'),
        'last_change_by_id': fields.Integer(required=True, description='Person identifier who changed the last time')
    })
