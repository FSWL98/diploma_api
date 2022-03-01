from flask import url_for
from flask_admin import Admin, helpers as admin_helpers
from flask_security.signals import user_registered
from flask_security import Security, SQLAlchemyUserDatastore

from ..model.entity.role import Role
from ..model.entity.staff import Staff

from . import view as views
import app.model.entity as entities
import app.model.relation as relations
from app.model.base import Base
from app.model.db import db

user_datastore = SQLAlchemyUserDatastore(db, Staff, Role)


def get_view(model_name, is_public):
    try:
        view = getattr(views, model_name + 'View')
    except AttributeError:
        view = views.UserView if is_public else views.AdminView
    return view


def add_views_by_module(admin, module):
    for class_name in dir(module):
        obj = getattr(module, class_name)
        try:
            if issubclass(obj, Base):
                admin.add_view(get_view(class_name, obj.is_public)(obj, db.session))
        except TypeError:  # If 'obj' is not a class
            pass


def init_app(app):
    security = Security(app, user_datastore)

    admin = Admin(app, name='Diploma', base_template='my_master.html', template_mode='bootstrap3')

    add_views_by_module(admin, entities)
    add_views_by_module(admin, relations)

    # Add the context processor
    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            get_url=url_for,
            h=admin_helpers
        )

    @user_registered.connect_via(app)
    def user_registered_sighandler(app, user, confirm_token):
        with db.auto_commit():
            user.active = False
            # default_role = user_datastore.find_role("read_only")
            # user_datastore.add_role_to_user(user, default_role)
