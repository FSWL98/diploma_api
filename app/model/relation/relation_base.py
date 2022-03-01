from datetime import datetime

from app.model.base import Base
from ...util import any_in

class RelationBase(Base):
    __abstract__ = True
    @classmethod
    def now(cls):
        return datetime.utcnow()

    @classmethod
    def _analyze_update(cls, old_ids, new_ids):
        old_ids = set(old_ids)
        new_ids = set(new_ids)
        to_add_ids = new_ids.difference(old_ids)
        to_delete_ids = old_ids.difference(new_ids)
        return to_add_ids, to_delete_ids

    @classmethod
    def _is_update_fields(cls, data):
        return any_in(cls.update_fields, data)

    def _update_simple_fields(self, data):
        self._update_fields(self.update_simple_fields, data)
        self.add()

    @classmethod
    def _sort_standard(cls, arg):
        return arg['id']
