from sqlalchemy import Column, DateTime, Integer, String

from app.model.db import seq
from .entity_base import EntityBase

class Criteria(EntityBase):
    __tablename__ = 'criteria'

    criteria_id = Column(Integer, seq, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    minimum = Column(Integer, nullable=False)
    maximum = Column(Integer, nullable=False)

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['criteria_id', 'name', 'description', 'minimum', 'maximum',
                            'create_date', 'update_date', 'last_change_by_id']

    update_fields = ['name', 'description', 'minimum', 'maximum', 'last_change_by_id']

    update_simple_fields = ['name', 'description', 'minimum', 'maximum', 'last_change_by_id']

    @classmethod
    def get_criteria_by_id(cls, criteria_id):
        return cls.dict_item(cls.query.filter_by(criteria_id=criteria_id).first())

    get_item_by_id = get_criteria_by_id

    @classmethod
    def get_criterias(cls):
        return [criteria.to_dict() for criteria in cls.query.order_by(cls.criteria_id).all()]

    get_items = get_criterias

    @classmethod
    def create(cls, data):
        criteria = cls(name=data['name'], description=data['description'], minimum=data['minimum'],
                       maximum=data['maximum'])

        criteria.add()
        criteria_dict = criteria.to_dict()

        return criteria_dict

    @classmethod
    def update(cls, data):
        criteria_dict = cls.get_criteria_by_id(data['criteria_id'])

        if criteria_dict is None:
            return None, f'Criteria with id {data["criteria_id"]} was not found'

        if not cls._is_update_fields(data):
            return criteria_dict

        criteria = cls.from_dict(criteria_dict)
        criteria._update_simple_fields(data)
        criteria_dict = criteria.to_dict()

        return criteria_dict

    @classmethod
    def delete(cls, criteria_id):
        criteria_dict = cls.get_criteria_by_id(criteria_id)
        if criteria_dict:
            cls._delete(criteria_dict)
            return criteria_dict
        return None, f'Criteria with id {criteria_id} was not found'
