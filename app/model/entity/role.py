from app.model.db import db
from .entity_base import EntityBase


class Role(EntityBase):
    __tablename__ = 'role'
    is_public = False

    role_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    level = db.Column(db.Integer(), default=0)

    create_date = db.Column(db.DateTime, default=EntityBase.now)
    update_date = db.Column(db.DateTime, default=EntityBase.now, onupdate=EntityBase.now)

    serialize_items_list = ['role_id', 'name', 'description', 'level', 'create_date', 'update_date']

    def __repr__(self):
        return "<Role(name='%s')>" % self.name

    @classmethod
    def get_roles(cls):
        return [role.to_dict() for role in cls.query.order_by(cls.role_id).all()]

    @classmethod
    def get_role_by_name(cls, name):
        return cls.dict_item(cls.query.filter_by(name=name).first())
