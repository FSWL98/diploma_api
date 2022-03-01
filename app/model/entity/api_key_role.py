from sqlalchemy import Column, DateTime, Integer, String

from app.model.db import seq
from .entity_base import EntityBase


class ApiKeyRole(EntityBase):
    __tablename__ = 'api_key_role'
    is_public = False

    api_key_role_id = Column(Integer, seq, primary_key=True)
    name = Column(String)
    level = Column(Integer)
    description = Column(String, default="")

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)

    serialize_items_list = ['api_key_role_id', 'name', 'level', 'description']

    @classmethod
    def get_api_key_role_by_id(cls, api_key_role_id):
        return cls.dict_item(cls.query.filter_by(api_key_role_id=api_key_role_id).first())

    get_item_by_id = get_api_key_role_by_id

    @classmethod
    def get_api_key_role_by_name(cls, api_key_role_name):
        return cls.dict_item(cls.query.filter(cls.name == api_key_role_name).first())

    @classmethod
    def get_api_key_roles_by_level(cls, api_key_role_level):
        return [api_key_role.to_dict() for api_key_role in cls.query.filter_by(level=api_key_role_level).
                order_by(cls.api_key_role_id).all()]

    @classmethod
    def get_api_key_roles(cls):
        return [api_key_role.to_dict() for api_key_role in cls.query.order_by(cls.api_key_role_id).all()]
