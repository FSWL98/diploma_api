from sqlalchemy import Column, DateTime, Integer, String, UnicodeText
from app.model.db import seq
from .entity_base import EntityBase


class Release(EntityBase):
    __tablename__ = 'release'

    release_id = Column(Integer, seq, primary_key=True)
    version = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(UnicodeText)
    release_date_utc = Column(DateTime, default=EntityBase.now)

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)

    serialize_items_list = ['release_id', 'version', 'name', 'description', 'release_date_utc', 'create_date',
                            'update_date']

    @classmethod
    def get_release_by_id(cls, release_id):
        return cls.dict_item(cls.query.filter_by(release_id=release_id).first())

    get_item_by_id = get_release_by_id
