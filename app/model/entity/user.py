import random
import string

from flask_security.utils import hash_password
from sqlalchemy import Boolean, Column, DateTime, Integer, ForeignKey, String

from app.model.db import db, seq
from .entity_base import EntityBase
from .person import Person
from ..relation.user_staff import UserStaff
from ...util.functions import handle_error


class User(EntityBase):
    __tablename__ = 'user'

    user_id = Column(Integer, seq, primary_key=True)

    person_id = Column(Integer, ForeignKey('person.person_id'))
    person = db.relationship('Person', backref='user')

    email = Column(String, unique=True)
    password = db.Column(String)
    is_valid_password = Column(Boolean, default=False, server_default='true')

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    get_relations_map = {
        'staff': lambda user_id: UserStaff.get_relation_ids_by_user(user_id)
    }

    serialize_items_list = ['user_id', 'person', 'email', 'is_valid_password',
                            'create_date', 'update_date', 'last_change_by_id']

    update_fields = ['email', 'is_valid_password', 'last_change_by_id']

    update_simple_fields = ['email', 'is_valid_password', 'last_change_by_id']

    delete_relations_funcs = [
        UserStaff.delete_relations_by_user
    ]

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.dict_item(cls.query.filter_by(user_id=user_id).first())

    get_item_by_id = get_user_by_id

    @classmethod
    def get_user_by_email(cls, email):
        return cls.dict_item(cls.query.filter_by(email=email).first())

    @classmethod
    def get_user_password(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        return user.password if user else None

    @classmethod
    def set_password(cls, user_id, new_password):
        user = cls.query.filter_by(user_id=user_id).first()
        if user is None:
            return None, f'User with id = {user_id} was not found'
        user.password = hash_password(new_password)
        user.is_valid_password = True
        user.add()
        return user.to_dict()

    @classmethod
    def get_active_users(cls):
        return [user.to_dict() for user in cls.query.filter(cls.is_bot_active==True).order_by(cls.user_id).all()]

    @classmethod
    def create(cls, data):
        if 'email' in data and cls.get_user_by_email(data['email']):
            return None, f'User with email {data["email"]} already exists'

        person = handle_error(Person.create(data['person']))
        if not person:
            return None, 'Person creation failed'

        if not data.get('password'):
            data['password'] = ''.join(random.choice(string.ascii_letters) for _ in range(16))
        else:
            data['is_valid_password'] = True
        user = cls(person_id=person['person_id'], email=data.get('email'), password=hash_password(data['password']),
                   is_valid_password=data.get('is_valid_password'), last_change_by_id=data.get('last_change_by_id'))

        user.add()
        user_dict = user.to_dict()
        return user_dict

    @classmethod
    def update(cls, data):
        user_dict = cls.get_user_by_id(data['user_id'])
        if user_dict is None:
            return None, f'User with id = {data["user_id"]} was not found'

        if data.get('person'):
            data['person']['person_id'] = user_dict['person']['person_id']
            person = handle_error(Person.update(data['person']))
            if not person:
                return None, 'Person updating failed'
            user_dict['person'] = person

        if not cls._is_update_fields(data):
            return user_dict

        if data.get('email') and user_dict['email'] != data['email'] and cls.get_user_by_email(data['email']):
            return None, f'User with email {data["email"]} already exists'

        user = cls.from_dict(user_dict)
        user._update_simple_fields(data)
        user_dict = user.to_dict()
        return user_dict

    @classmethod
    def update_email(cls, user_id, email):
        user_dict = cls.get_user_by_id(user_id)
        if user_dict is None:
            return None, f'User with id = {user_id} was not found'
        if user_dict['email'] != email and cls.get_user_by_email(email):
            return None, f'User with email {email} already exists'
        user = cls.from_dict(user_dict)
        user.email = email
        user.add()
        return user.to_dict()

    @classmethod
    def set_is_active(cls, user_id, is_bot_active):
        user_dict = cls.get_user_by_id(user_id)
        if user_dict is None:
            return None, f'User with id = {user_id} was not found'
        user = cls.from_dict(user_dict)
        user.is_bot_active = is_bot_active
        user.add()
        user_dict = user.to_dict()
        Person.refresh_notification_method(user_dict['person']['person_id'])
        return user_dict

    @classmethod
    def delete(cls, user_id):
        user_dict = cls.get_user_by_id(user_id)
        if user_dict:
            cls._delete(user_dict)
            Person.delete(user_dict['person']['person_id'])
            return user_dict
        return None, f'User with id = {user_id} was not found'
