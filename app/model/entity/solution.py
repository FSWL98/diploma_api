from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.model.db import seq
from ..entity.mark import Mark
from .entity_base import EntityBase
from ..relation.user_event import UserEvent


class Solution(EntityBase):
    __tablename__ = 'solution'

    solution_id = Column(Integer, seq, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    event_id = Column(Integer, ForeignKey('Event.event_id'))
    user_event_id = Column(Integer, ForeignKey('user_event.user_event_id'))
    url = Column(String)
    description = Column(String, nullable=True)

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['solution_id', 'user_event_id', 'url', 'description', 'create_date',
                            'update_date', 'last_change_by_id']

    update_fields = ['url', 'description', 'last_change_by_id']

    update_simple_fields = ['url', 'description', 'last_change_by_id']

    get_relations_map = {
        'marks': lambda solution_id: Mark.get_marks_by_solution(solution_id)
    }

    delete_relations_funcs = [
        Mark.delete_by_solution,
    ]

    @classmethod
    def get_solution_by_id(cls, solution_id):
        return cls.dict_item(cls.query.filter_by(solution_id=solution_id).first())

    get_item_by_id = get_solution_by_id

    @classmethod
    def get_solution_by_user_event(cls, user_event_id):
        return cls.dict_item(cls.query.filter_by(user_event_id=user_event_id).first())

    @classmethod
    def get_solution_by_user_and_event(cls, user_id, event_id):
        return cls.dict_item(cls.query.filter_by(user_id=user_id, event_id=event_id).first())

    @classmethod
    def get_solutions_by_event(cls, event_id):
        user_event_ids = UserEvent.get_relation_ids_by_event(event_id)
        return [cls.get_solution_by_user_event(user_event_id) for user_event_id in user_event_ids]

    @classmethod
    def get_solutions_by_user(cls, user_id):
        user_event_ids = UserEvent.get_relation_ids_by_user(user_id)
        return [cls.get_solution_by_user_event(user_event_id) for user_event_id in user_event_ids]

    @classmethod
    def create(cls, data):
        user_event = UserEvent.get_relation(data['user_id'], data['event_id'])
        if user_event is None:
            return None, f'User {data["user_id"]} is not registered for event {data["event_id"]}'

        solution = cls(user_id=data['user_id'], event_id=data['event_id'], user_event_id=user_event['user_event_id'],
                       url=data['url'], description=data['description'], last_change_by_id=data['last_change_by_id'])
        solution.add()
        solution_dict = solution.to_dict()

        return solution_dict

    @classmethod
    def update(cls, data):
        solution_dict = cls.get_solution_by_id(data['solution_id'])

        if solution_dict is None:
            return None, f'Solution with id {data["solution_id"]} was not found'

        if not cls._is_update_fields(data):
            return solution_dict

        solution = cls.from_dict(solution_dict)
        solution._update_simple_fields(data)
        solution_dict = solution.to_dict()

        return solution_dict

    @classmethod
    def delete(cls, solution_id):
        solution_dict = cls.get_solution_by_id(solution_id)
        if solution_dict:
            cls._delete(solution_dict)
            return solution_dict
        return None, f'Solution with id {solution_id} was not found'

