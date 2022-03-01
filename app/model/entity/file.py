import os

from sqlalchemy import Column, DateTime, Integer, String

from .entity_base import EntityBase
from ...util.file import get_file_formats
from ...util.image import get_media_url, get_media_path
from app.model.db import seq


class File(EntityBase):
    __abstract__ = True

    file_id = Column(Integer, seq, primary_key=True)
    url = Column(String)
    filename = Column(String)
    type = Column(String)
    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)

    last_change_by_id = Column(Integer)

    serialize_items_list = ['file_id', 'url', 'filename', 'type', 'create_date', 'update_date', 'last_change_by_id']

    update_fields = ['url', 'filename', 'type', 'last_change_by_id']

    update_simple_fields = ['url', 'filename', 'last_change_by_id']

    file_mime_types, file_extensions = get_file_formats()

    all_file_mime_types = list(set([__ for _ in list(file_mime_types.values()) for __ in _]))

    @classmethod
    def get_file_by_id(cls, file_id):
        return cls.dict_item(cls.query.filter_by(file_id=file_id).first())

    @classmethod
    def get_file_by_name(cls, filename):
        return cls.dict_item(cls.query.filter_by(filename=filename).first())

    get_item_by_id = get_file_by_id

    @classmethod
    def get_files(cls):
        return [file.to_dict() for file in cls.query.order_by(cls.file_id).all()]

    @classmethod
    def check_file_mime_type(cls, file, type_):
        return file.mimetype in cls.file_mime_types[type_]

    @classmethod
    def get_file_type(cls, mimetype):
        for type_ in cls.file_mime_types:
            if mimetype in cls.file_mime_types[type_]:
                return type_

    @classmethod
    def get_save_filename(cls, file_dict):
        return f"{file_dict['user_id']}_{file_dict['filename']}"

    @classmethod
    def get_file_path(cls, file_dict):
        return get_media_path(file_dict['type'], cls.get_save_filename(file_dict))

    @classmethod
    def get_file_url(cls, file_dict):
        return get_media_url(file_dict['type'], cls.get_save_filename(file_dict))

    @classmethod
    def _analyze_update(cls, old_ids, new_ids):
        old_ids = set(old_ids)
        new_ids = set(new_ids)
        to_add_ids = new_ids.difference(old_ids)
        to_delete_ids = old_ids.difference(new_ids)
        return to_add_ids, to_delete_ids

    @classmethod
    def __delete_file(cls, file_dict):
        file_path = cls.get_file_path(file_dict)
        if os.path.exists(file_path):
            os.remove(file_path)

    @classmethod
    def delete(cls, file_id):
        file_dict = cls.get_file_by_id(file_id)
        if file_dict:
            cls.__delete_file(file_dict)
            cls._delete(file_dict)
            return file_dict
        return None
