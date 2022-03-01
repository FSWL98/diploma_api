from flask import redirect, url_for
from flask_security import current_user

from .base_view import BaseView


class UserView(BaseView):
    deletable = False

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('security.login'))

        self.can_delete = self.deletable or current_user.has_role('admin')
        self.can_edit = True
        if current_user.has_role('read_only'):
            self.can_delete = False
            self.can_edit = False

    def is_action_allowed(self, name):
        if name == 'delete':
            return current_user.has_role('admin')
        return super(UserView, self).is_action_allowed(name)


class AdminView(BaseView):
    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('security.login'))
