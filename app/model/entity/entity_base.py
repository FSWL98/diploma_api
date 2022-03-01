from collections import OrderedDict
from datetime import date, datetime
from flask import current_app
from sqlalchemy.inspection import inspect

from app.model.base import Base
from ...util import any_in


class EntityBase(Base):
    __abstract__ = True

    get_relations_map = {}

    update_fields = []
    update_simple_fields = []
    update_relations_map = {}

    delete_relations_funcs = []

    @classmethod
    def now(cls):
        return datetime.utcnow()

    @classmethod
    def today(cls):
        return date.today()

    @classmethod
    def get_item_by_id(cls, item_id):
        pass

    @classmethod
    def get_items(cls, page_id=0, page_size=-1, filter_func=None, base_query=None):
        MAX_PAGE_SIZE = current_app.config['MAX_PAGE_SIZE']
        query = base_query if base_query else cls.query.order_by(inspect(cls).primary_key[0].name)
        if filter_func:
            query = filter_func(query)
        if page_size < 0:
            page_id = 0
            page_size = MAX_PAGE_SIZE
        elif page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE
            page_id %= MAX_PAGE_SIZE

        query = query.paginate(page_id+1, page_size, False)
        return [item.to_dict() for item in query.items], query.total

    @classmethod
    def get_relations(cls, item_id, items=None):
        result = OrderedDict([(cls.__table__.columns.keys()[0], item_id)])
        for key, func in cls.get_relations_map.items():
            if items is None or key in items:
                result.update({key: func(item_id)})
        return result

    @classmethod
    def _is_update_fields(cls, data):
        return any_in(cls.update_fields, data)

    def _update_simple_fields(self, data):
        self._update_fields(self.update_simple_fields, data)
        self.add()

    def _update_relations(self, data):
        for key, func in self.update_relations_map.items():
            if key in data:
                func(self, data[key])

    @classmethod
    def _delete(cls, item_dict):
        item = cls.from_dict(item_dict)
        item_id = getattr(item, cls.__table__.columns.keys()[0])
        for delete_func in cls.delete_relations_funcs:
            delete_func(item_id)
        item.delete_self()
        cls._delete_from_cache(item_dict)

    @classmethod
    def _delete_from_cache(cls, item):
        pass

    @classmethod
    def get_standard_id(cls):
        return cls.__table__.columns.keys()[0]

    @classmethod
    def _sort_standard(cls, arg):
        return arg[cls.get_standard_id()]
