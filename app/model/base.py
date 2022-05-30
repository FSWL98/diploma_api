from collections import OrderedDict
from datetime import date, datetime, time, timedelta
from dateutil import parser

from ..util.dt import datetime_to_str, validate_iso8601, timedelta_to_dict
from app.model.db import db, merge


class Base(db.Model):
    __abstract__ = True

    serialize_items_list = []

    to_dict_entity = dict()

    from_dict_entity = dict()

    is_public = True

    def to_dict(self, items=None):
        def dictionate_entity(entity):
            if isinstance(entity, list):
                entity = list(entity)
                for i in range(len(entity)):
                    entity[i] = dictionate_entity(entity[i])
            if isinstance(entity, date):
                return entity.isoformat()
            elif isinstance(entity, datetime):
                return datetime_to_str(entity)
            elif isinstance(entity, time):
                return entity.strftime('%H:%M')
            elif isinstance(entity, timedelta):
                return timedelta_to_dict(entity)
            elif 'to_dict' in dir(entity):
                return entity.to_dict()
            else:
                return entity

        return OrderedDict([(key, self.to_dict_entity[key](getattr(self, key)) if key in self.to_dict_entity
                             else dictionate_entity(getattr(self, key)))
                           for key in (self.serialize_items_list if items is None else items)])

    @classmethod
    def dict_item(cls, item):
        if item is None:
            return None
        return item.to_dict()

    @classmethod
    def from_dict(cls, data):
        item = cls()
        item._update_fields(cls.__table__.columns.keys(), data)
        return merge(item)

    def _update_fields(self, fields, data):
        for field in fields:
            if field in data:
                try:
                    python_type = self.__table__.columns[field].type.python_type
                except NotImplementedError:
                    python_type = None
                if python_type == time:
                    if validate_iso8601(data[field]):
                        setattr(self, field, parser.parse(data[field]).time())
                elif python_type == datetime:
                    if isinstance(data[field], datetime):
                        setattr(self, field, data[field])
                    elif validate_iso8601(data[field]):
                        setattr(self, field, parser.parse(data[field]))
                elif python_type == date:
                    if validate_iso8601(data[field]):
                        setattr(self, field, parser.parse(data[field]).date())
                elif python_type == timedelta:
                    try:
                        setattr(self, field, timedelta(**data[field]))
                    except Exception:
                        continue
                else:
                    setattr(self, field,
                            self.from_dict_entity[field](data[field]) if field in self.from_dict_entity
                            else data[field])

    def add(self):
        with db.auto_commit():
            db.session.add(self)

    def delete_self(self):
        with db.auto_commit():
            db.session.delete(self)
