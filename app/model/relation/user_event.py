from sqlalchemy import Column, Integer, String, Index

from .relation_base import RelationBase
from app.model.db import seq


class UserEvent(RelationBase):
    __tablename__ = 'user_event'

    user_event_id = Column(Integer, seq, primary_key=True)
    user_id = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)

    idx = Index('idx_user_event', user_event_id, user_id, event_id)

    serialize_items_list = ['user_event_id', 'user_id', 'event_id']

    @classmethod
    def get_relation_by_id(cls, user_event_id):
        return cls.dict_item(cls.query.filter_by(user_event_id=user_event_id).first())

    @classmethod
    def get_relation(cls, user_id, event_id):
        return cls.dict_item(cls.query.filter_by(user_id=user_id, event_id=event_id).first())

    @classmethod
    def get_relations_by_user(cls, user_id):
        return [relation.to_dict() for relation in
                cls.query.filter_by(user_id=user_id).order_by(cls.user_event_id).all()]

    @classmethod
    def get_relation_ids_by_user(cls, user_id):
        return [relation['user_event_id'] for relation in cls.get_relations_by_user(user_id)]

    @classmethod
    def get_relations_by_event(cls, event_id):
        return [relation.to_dict() for relation in
                cls.query.filter_by(event_id=event_id).order_by(cls.user_event_id).all()]

    @classmethod
    def get_relation_ids_by_event(cls, event_id):
        return [relation['user_event_id'] for relation in cls.get_relations_by_event(event_id)]

    @classmethod
    def create_by_id(cls, user_id, event_id):
        relation_dict = cls.get_relation(user_id, event_id)
        if relation_dict is None:
            relation = cls(user_id=user_id, event_id=event_id)
            relation.add()
            relation_dict = relation.to_dict()
        return relation_dict

    @classmethod
    def create(cls, data):
        return cls.create_by_id(data['user_id'], data['event_id'])

    @classmethod
    def __delete_relation(cls, relation_dict):
        relation = cls.from_dict(relation_dict)
        relation.delete_self()

    @classmethod
    def delete(cls, relation_id):
        relation_dict = cls.get_relation_by_id(relation_id)
        if relation_dict:
            cls.__delete_relation(relation_dict)

    @classmethod
    def delete_relation(cls, user_id, event_id):
        relation_dict = cls.get_relation(user_id, event_id)
        if not relation_dict:
            return None, f'Relation with event id = {event_id} and user id = {user_id} was not found'
        cls.__delete_relation(relation_dict)
        return relation_dict

    @classmethod
    def delete_relations_by_user(cls, user_id):
        relation_dicts = cls.get_relations_by_user(user_id)
        for relation_dict in relation_dicts:
            cls.__delete_relation(relation_dict)

    @classmethod
    def delete_relations_by_event(cls, event_id):
        relation_dicts = cls.get_relations_by_event(event_id)
        for relation_dict in relation_dicts:
            cls.__delete_relation(relation_dict)
