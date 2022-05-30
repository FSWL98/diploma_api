from os import environ as env

from flask_security import UserMixin
from flask_security.utils import hash_password
from sqlalchemy import Boolean, Column, DateTime, event, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import array_agg

from app.model.db import db, seq
from .entity_base import EntityBase
from .person import Person
from .role_staff import role_staff_table
from ..relation.user_staff import UserStaff
from ...util.functions import handle_error


class Staff(EntityBase, UserMixin):
    __tablename__ = 'staff'

    id = Column(Integer, seq, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.person_id'))
    person = db.relationship('Person', backref='staff')
    email = Column(String, unique=True)
    password = db.Column(String, nullable=False)
    active = Column(Boolean, default=False)
    roles = db.relationship('Role', secondary=role_staff_table, backref='staff', lazy=True)

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['id', 'person', 'email', 'active', 'roles', 'create_date',
                            'update_date', 'last_change_by_id']

    update_fields = ['email', 'active', 'roles', 'last_change_by_id']

    update_simple_fields = ['email', 'active', 'last_change_by_id']

    get_relations_map = {
        'users': lambda id: UserStaff.get_relation_ids_by_staff(id)
    }

    delete_relations_funcs = [
        UserStaff.delete_relations_by_staff
    ]

    @classmethod
    def get_staffs(cls):
        return [staff.to_dict() for staff in cls.query.order_by(cls.id).all()]

    get_items = get_staffs

    @classmethod
    def get_staff_instance_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_staff_by_id(cls, id):
        return cls.dict_item(cls.query.filter_by(id=id).first())

    get_item_by_id = get_staff_by_id

    @classmethod
    def get_staff_by_email(cls, email):
        return cls.dict_item(cls.query.filter_by(email=email).first())

    @classmethod
    def get_staff_password(cls, id):
        staff = cls.query.filter_by(id=id).first()
        return staff.password if staff else None

    @classmethod
    def by_roles_filter(cls, roles):
        def f(query):
            return query.join(role_staff_table).filter(role_staff_table.c.role_id.in_(roles)).group_by(cls.id). \
                having(array_agg(role_staff_table.c.role_id).contains(roles))

        return f

    @classmethod
    def create(cls, data):
        from ...admin import user_datastore

        if cls.get_staff_by_email(data['email']):
            return None, f'Staff with email {data["email"]} already exists'

        person = handle_error(Person.create(data['person']))
        if not person:
            return None, 'Person creation failed'

        staff = cls(person_id=person['person_id'], email=data['email'],
                    password=hash_password(data['password']), active=data.get('active') == True)
        staff.add()
        staff_dict = staff.to_dict()

        if data.get('roles'):
            with db.auto_commit():
                for role_name in data['roles']:
                    role = user_datastore.find_role(role_name)
                    if role:
                        person = user_datastore.find_user(email=data['email'])
                        user_datastore.add_role_to_user(person, role)

        return staff_dict

    @classmethod
    def _analyze_update(cls, old_ids, new_ids):
        old_ids = set(old_ids)
        new_ids = set(new_ids)
        to_add_ids = new_ids.difference(old_ids)
        to_delete_ids = old_ids.difference(new_ids)
        return to_add_ids, to_delete_ids

    @classmethod
    def update(cls, data):
        from ...admin import user_datastore

        staff_dict = cls.get_staff_by_id(data['id'])
        if staff_dict is None:
            return None, f'Staff with id = {data["id"]} was not found'
        if not cls._is_update_fields(data):
            return staff_dict

        if data.get('email') and staff_dict['email'] != data['email']:
            if cls.get_staff_by_email(data['email']):
                return None, f'Staff with email {data["email"]} already exists'

        if data.get('person'):
            data['person']['person_id'] = staff_dict['person']['person_id']
            person = handle_error(Person.update(data['person']))
            if not person:
                return None, 'Person updating failed'

        staff = cls.from_dict(staff_dict)
        staff._update_simple_fields(data)
        staff_dict = staff.to_dict()

        if data.get('roles'):
            to_add_roles, to_delete_roles = cls._analyze_update([role['name'] for role in staff_dict['roles']],
                                                                data['roles'])
            person = user_datastore.find_user(id=data['id'])
            with db.auto_commit():
                for role in filter(lambda role_dict: role_dict['name'] in to_delete_roles, staff_dict['roles']):
                    role_name = user_datastore.find_role(role['name'])
                    user_datastore.remove_role_from_user(person, role_name)
                for to_add_role in to_add_roles:
                    role = user_datastore.find_role(to_add_role)
                    user_datastore.add_role_to_user(person, role)

        return staff_dict

    @classmethod
    def set_password(cls, id, new_password):
        staff = cls.get_staff_instance_by_id(id)
        if staff is None:
            return None, f'Staff with id = {id} was not found'
        staff.password = hash_password(new_password)
        staff.add()
        return staff.to_dict()

    @classmethod
    def set_active(cls, id, active=True):
        staff_dict = cls.get_staff_by_id(id)
        if staff_dict is None:
            return None, f'Staff with id = {id} was not found'
        staff = cls.from_dict(staff_dict)
        staff.active = active
        staff.add()
        return staff.to_dict()

    @classmethod
    def delete(cls, id):
        staff_dict = cls.get_staff_by_id(id)
        if staff_dict:
            cls._delete(staff_dict)
            Person.delete(staff_dict['person']['person_id'])
            return staff_dict
        return None, f'Staff with id = {id} was not found'


@event.listens_for(Staff.__table__, 'after_create')
def create_all(*args, **kwargs):
    with db.auto_commit():
        print('rofl')
        person = Person.create(dict(name=env['DEFAULT_USER_NAME'], surname=env['DEFAULT_USER_SURNAME']))
        db.session.add(Staff(email=env['ADMIN_LOGIN'], password=env['ADMIN_PASSWORD'], active=True,
                             person_id=person['person_id']))
