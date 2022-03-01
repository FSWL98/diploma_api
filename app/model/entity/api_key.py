import uuid
from flask import current_app
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from .entity_base import EntityBase


def get_default_expire_date():
    return datetime.utcnow() + timedelta(days=current_app.config['API_TOKEN_DAYS_ACTIVE'])


class ApiKey(EntityBase):
    __tablename__ = 'api_key'
    is_public = False

    key = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True)
    description = Column(String)
    expire_date = Column(DateTime, default=get_default_expire_date)
    role_id = Column(Integer, ForeignKey('api_key_role.api_key_role_id'))

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)

    serialize_items_list = ['key', 'name', 'description', 'expire_date', 'role_id']

    @classmethod
    def get_api_key_by_key(cls, key):
        return cls.dict_item(cls.query.filter_by(key=key).first())

    get_item_by_id = get_api_key_by_key

    # @classmethod
    # def get_api_keys(cls):
    #     return [api_key.to_dict() for api_key in cls.query.all()]
    #
    # get_items = get_api_keys

    @classmethod
    def get_api_key_by_name(cls, name):
        return cls.dict_item(cls.query.filter_by(name=name).first())

    @classmethod
    def delete(cls, key):
        api_key_dict = cls.get_api_key_by_key(key)
        if api_key_dict:
            cls._delete(api_key_dict)
            return api_key_dict
        return None
