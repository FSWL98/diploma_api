import os

from flask import current_app, Markup
from flask_admin import form
from wtforms import validators

from .permissions_view import UserView
from ...util.file import get_file_formats
from ...util.image import get_media_path, get_media_url


class FileView(UserView):
    deletable = True

    file_mime_types, file_extensions = get_file_formats()

    def get_save_filename_func(self, _form):
        return _form.file.data.filename

    def _format_url(self, context, model, name):
        if model.type == 'image':
            return Markup('<img src="%s" width="100">' % model.url)

        if model.type == 'audio':
            return Markup('<audio controls="controls"><source src="%s" type="audio/mpeg" /></audio>' % model.url)

        if model.type == 'video':
            sources = ''
            for video_type in self.file_mime_types['video']:
                sources += f'<source src="{model.url}" type="{video_type}">'
            return Markup('<video width="250" height="200" controls>' + sources + '</video>')

        return model.url

    images_ext = file_extensions['image']
    audios_ext = file_extensions['audio']
    videos_ext = file_extensions['video']
    documents_ext = file_extensions['document']

    def get_type_from_extension(self, ext):
        if ext in self.images_ext:
            return 'image'
        elif ext in self.audios_ext:
            return 'audio'
        elif ext in self.videos_ext:
            return 'video'
        elif ext in self.documents_ext:
            return 'document'
        return None

    form_extra_fields = {
        'file': form.FileUploadField('file', allowed_extensions=images_ext + audios_ext + videos_ext + documents_ext)
    }

    column_formatters = {
        'url': _format_url
    }

    def _change_path_data(self, _form):
        try:
            storage_file = _form.file.data

            if storage_file is not None:
                ext = storage_file.filename.split('.')[-1]
                _form.type.data = self.get_type_from_extension(ext)

                save_filename = self.get_save_filename_func(_form)
                save_path = get_media_path(_form.type.data, save_filename)
                storage_file.save(save_path)
                file_size = os.stat(save_path).st_size

                if file_size > current_app.config[f"MAX_{_form.type.data.upper()}_SIZE"]:
                    os.remove(save_path)
                    raise validators.ValidationError("File is too big")

                _form.filename.data = _form.filename.data or storage_file.filename
                _form.url.data = get_media_url(_form.type.data, save_filename)

                del _form.file

        except Exception as ex:
            if ex.__class__ == validators.ValidationError:
                raise ex
            pass

        return _form

    def edit_form(self, obj=None):
        return self._change_path_data(
            super(FileView, self).edit_form(obj)
        )

    def create_form(self, obj=None):
        return self._change_path_data(
            super(FileView, self).create_form(obj)
        )
