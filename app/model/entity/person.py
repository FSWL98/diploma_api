import jwt

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask import jsonify
from sqlalchemy import Column, DateTime, Integer, String, Boolean

from app.model.db import seq
from .entity_base import EntityBase


class Person(EntityBase):
    __tablename__ = 'person'
    is_public = False

    person_id = Column(Integer, seq, primary_key=True)

    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    gender = Column(String)
    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['person_id', 'name', 'surname', 'patronymic', 'gender',
                            'create_date', 'update_date', 'last_change_by_id']

    update_fields = ['name', 'surname', 'patronymic', 'gender',
                     'create_date', 'update_date', 'last_change_by_id']

    update_simple_fields = ['name', 'surname', 'patronymic', 'gender',
                            'create_date', 'update_date', 'last_change_by_id']

    def __repr__(self):
        return f"<Person(name='{self.name}', surname='{self.surname}')>"

    @classmethod
    def get_email_by_person(cls, person_id):
        person_dict = cls.get_person_by_id(person_id)
        person = cls.from_dict(person_dict)
        if len(person.user) > 0:
            return person.user[0].email
        if len(person.staff) > 0:
            return person.staff[0].email
        return None

    @classmethod
    def get_person_by_id(cls, person_id):
        return cls.dict_item(cls.query.filter_by(person_id=person_id).first())

    get_item_by_id = get_person_by_id

    @classmethod
    def get_item_obj(cls, person_id):
        return cls.query.filter_by(person_id=person_id).first()

    @classmethod
    def create(cls, data):
        person = cls(name=data.get('name'), surname=data.get('surname'), patronymic=data.get('patronymic'),
                     gender=data.get('gender'))
        person.add()
        person_dict = person.to_dict()
        return person_dict

    @classmethod
    def update(cls, data):
        person_dict = cls.get_person_by_id(data['person_id'])
        if person_dict is None:
            return None, f'Person with id = {data["person_id"]} was not found'

        if not cls._is_update_fields(data):
            return person_dict
        person = cls.from_dict(person_dict)
        person._update_simple_fields(data)
        person_dict = person.to_dict()
        return person_dict

    @classmethod
    def delete(cls, person_id):
        person_dict = cls.get_person_by_id(person_id)
        if person_dict:
            cls._delete(person_dict)
            return person_dict
        return None, f'Person with id = {person_id} was not found'

    @staticmethod
    def encode_access_token(person_id, staff_id=None, user_id=None, password=False, refresh=True):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'person_id': person_id,
                'staff_id': staff_id,
                'user_id': user_id,
                'password': password,
                'refresh': False
            }
            access_token = create_access_token(identity=payload)
            if refresh:
                payload['refresh'] = True
                refresh_token = create_refresh_token(identity=payload)
                return jsonify(access_token=access_token, refresh_token=refresh_token)
            elif password:
                return jsonify(password_reset_token=access_token)
            else:
                return jsonify(access_token=access_token)
        except Exception as e:
            return e

    @staticmethod
    def decode_access_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        """
        try:
            payload = decode_token(auth_token)
            return payload
        except jwt.ExpiredSignatureError:
            return None, 'Expired token supplied'
        except jwt.InvalidTokenError:
            return None, 'Invalid token supplied'
