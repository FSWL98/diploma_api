from sqlalchemy import Column, DateTime, Integer, String

from app.model.db import seq
from .entity_base import EntityBase


class Event(EntityBase):
    __tablename__ = 'Event'

    event_id = Column(Integer, seq, primary_key=True)
    name = Column(String, nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    evaluation_method = Column(String, default='simple')

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['event_id', 'name', 'date_start', 'date_end', 'evaluation_method', 'create_date',
                            'update_date', 'last_change_by_id']
    update_fields = ['name', 'date_start', 'date_end', 'evaluation_method', 'last_change_by_id']
    update_simple_fields = ['name', 'date_start', 'date_end', 'evaluation_method', 'last_change_by_id']

    @classmethod
    def get_event_by_id(cls, event_id):
        return cls.dict_item(cls.query.filter_by(event_id=event_id).first())

    get_item_by_id = get_event_by_id

    @classmethod
    def get_events(cls):
        return [event.to_dict() for event in cls.query.order_by(cls.event_id).all()]

    get_items = get_events

    @classmethod
    def create(cls, data):
        event = cls(name=data['name'], date_start=data['date_start'], date_end=data['date_end'],
                    evaluation_method=data['evaluation_method'])
        event.add()
        event_dict = event.to_dict()

        return event_dict

    @classmethod
    def update(cls, data):
        event_dict = cls.get_event_by_id(data['event_id'])

        if event_dict is None:
            return None, f'Event with id {data["event_id"]} was not found'

        if not cls._is_update_fields(data):
            return event_dict

        event = cls.from_dict(event_dict)
        event._update_simple_fields(data)
        event_dict = event.to_dict()

        return event_dict

    @classmethod
    def delete(cls, event_id):
        event_dict = Event.get_event_by_id(event_id)
        if event_dict:
            cls._delete(event_dict)
            return event_dict
        return None, f'Event with id {event_id} was not found'
