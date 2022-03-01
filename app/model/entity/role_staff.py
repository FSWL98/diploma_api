from os import environ as env
from sqlalchemy import event
from app.model.db import db

role_staff_table = db.Table('role_staff',
                            db.Column('staff_id', db.Integer(), db.ForeignKey('staff.id')),
                            db.Column('role_id', db.Integer(), db.ForeignKey('role.role_id')))


@event.listens_for(role_staff_table, 'after_create')
def create_all(*args, **kwargs):
    from ...admin import user_datastore

    with db.auto_commit():
        admin_role = user_datastore.find_role("admin")
        admin_user = user_datastore.find_user(email=env['ADMIN_LOGIN'])
        user_datastore.add_role_to_user(admin_user, admin_role)
