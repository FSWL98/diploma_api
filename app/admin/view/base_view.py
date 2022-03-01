import json
from flask import flash
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from jinja2 import Markup
from sqlalchemy.inspection import inspect
from wtforms import fields

from app.model import entity
from app.model import relation
from app.util.functions import handle_error


def get_formatter_default_func(additional_column):
    def formatter(view, context, model, name):
        item_id = getattr(model, additional_column['name'] + '_id')
        item = additional_column['model'].get_item_by_id(item_id)
        if item is not None:
            return item[additional_column['target_column']]
        return None
    return formatter


def _format_datetime(self, context, model, name):
    datetime_field = getattr(model, name)
    return datetime_field.strftime("%d.%m.%Y %H:%M") if datetime_field else None


def json_formatter(view, value):
    json_value = json.dumps(value, ensure_ascii=False, indent=2)
    return Markup('<pre>{}</pre>'.format(json_value))


MY_FORMATTERS = typefmt.BASE_FORMATTERS.copy()
MY_FORMATTERS[dict] = json_formatter


class BaseView(ModelView):
    def __init__(self, model, *args, **kwargs):
        self.column_display_pk = True
        self.column_formatters['create_date'] = _format_datetime
        self.column_formatters['update_date'] = _format_datetime

        if self.form_excluded_columns is None:
            self.form_excluded_columns = ('update_date',)
        else:
            self.form_excluded_columns += ('update_date',)

        if self.column_list is None and len(self.additional_columns) > 0:
            self.column_list = tuple(model.__table__.columns)

        self.form_overrides = self.form_overrides or {}

        for additional_column in self.additional_columns:
            self.column_list += (additional_column['name'],)
            if additional_column.get('formatter') is None:
                formatter = get_formatter_default_func(additional_column)
            else:
                formatter = additional_column['formatter']
            self.column_formatters[additional_column['name']] = formatter
            if additional_column.get('model') is not None:
                self.form_overrides[f"{additional_column['base_column']}"] = fields.SelectField

        super(BaseView, self).__init__(model, *args, **kwargs)

    column_type_formatters = MY_FORMATTERS
    can_set_page_size = True
    can_export = True
    additional_columns = []

    def handle_choice(self, _form):
        for additional_column in self.additional_columns:
            if additional_column.get('model') is None:
                continue
            col = getattr(_form, additional_column['base_column'])
            items = additional_column['model'].get_items()
            if isinstance(items, tuple):
                items = items[0]
            col.choices = [(_[additional_column['base_column']], _[additional_column['target_column']]) for
                           _ in items]
            if len(col.validators) > 0 and col.validators[0].field_flags[0] == 'optional':
                col.choices.append((None, ''))
            if col.data == 'None':
                col.data = None
                col.validate_choice = False
        return _form

    def edit_form(self, obj=None):
        return self.handle_choice(super(BaseView, self).edit_form(obj))

    def create_form(self, obj=None):
        return self.handle_choice(super(BaseView, self).create_form(obj))

    def create_model(self, form):
        try:
            if hasattr(entity, self.model.__name__):
                ModelClass = getattr(entity, self.model.__name__)
            else:
                ModelClass = getattr(relation, self.model.__name__)
            data = {field_name: field.data for field_name, field in form._fields.items()}
            model_dict = handle_error(ModelClass.create(data))
            if model_dict is None:
                flash(gettext('Failed to create record'))
                return False
            else:
                model = self.build_new_instance()
                form.populate_obj(model)
                self._on_model_change(form, model, True)
                self.after_model_change(form, model, False)
                return model
        except Exception as ex:
            flash(gettext('Exception while creating record'))
            return super(BaseView, self).create_model(form)

    def update_model(self, form, model):
        # try:
        #     self._on_model_change(form, model, False)
        #     EntityClass = getattr(entity, type(model).__name__)
        #     pk_name = inspect(EntityClass).primary_key[0].name
        #     pk_value = getattr(model, pk_name)
        #     data = {field_name: field.data for field_name, field in form._fields.items()}
        #     data[pk_name] = pk_value
        #     if not EntityClass.update(data):
        #         flash(gettext('Failed to update record'))
        #         return False
        #     else:
        #         self.after_model_change(form, model, False)
        #         return True
        # except AttributeError as ex:
        return handle_error(super(BaseView, self).update_model(form, model))

    def delete_model(self, model):
        """
            Delete model.
            :param model:
                Model to delete
        """
        try:
            self.on_model_delete(model)
            try:
                EntityClass = getattr(entity, type(model).__name__)
                pk_name = inspect(EntityClass).primary_key[0].name
                EntityClass.delete(getattr(model, pk_name))
            except Exception as e:
                flash(gettext('Exception while deleting record'))
                self.session.flush()
                self.session.delete(model)
                self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')

            self.session.rollback()

            return False
        else:
            self.after_model_delete(model)

        return True
