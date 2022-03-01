import base64
import hmac
import json
import os
import random
import string

import pandas as pd
import re
import requests
import uuid

from copy import deepcopy
from flask import Response, current_app, send_file
from hashlib import sha1
from http import HTTPStatus
from statistics import mean as stat_mean
from sqlalchemy.inspection import inspect


def delete_from_dict(dictionary, fields):
    for f in fields:
        if dictionary.get(f):
            del dictionary[f]
    return dictionary


def get_primary_key(model):
    from app.model import entity

    EntityClass = getattr(entity, type(model).__name__)
    pk_name = inspect(EntityClass).primary_key[0].name
    return getattr(model, pk_name)


def get_file(url, filepath):
    try:
        img_data = requests.get(url).content
        with open(filepath, 'wb') as handler:
            handler.write(img_data)
        return url
    except Exception as e:
        print(f"Error getting image: {str(e)}. Url: {url}")
        return None


def get_version():
    with open('VERSION') as version_file:
        version = version_file.read()
    return version.strip()


def get_test_data():
    with open(os.path.join('app', 'model', 'test_data.json'), encoding='utf-8') as test_data_file:
        test_data = json.load(test_data_file)
    return test_data


def all_in(params, data):
    return all(p in data for p in params)


def any_in(params, data):
    return any(p in data for p in params)


def get_page_params(page_id, page_size, count):
    if page_size == -1:
        return 0, count
    else:
        return max(page_id * page_size, 0), max((page_id + 1) * page_size, 0)


def get_filters(filters_data, filters_dict):
    filters = []
    for key in filters_dict.keys():
        if key not in filters_data:
            continue
        if isinstance(filters_dict[key], dict):
            if len(filters_data[key].split()) != 2:
                continue
            key1, value = filters_data[key].split()
            if key1 in filters_dict[key] and value.isdigit():
                filters.append(filters_dict[key][key1](int(value)))
        else:
            filters.append(filters_dict[key](filters_data[key]))
    return filters


def get_filter_func(filters_data, filters_dict):
    filters = get_filters(filters_data, filters_dict)
    return lambda item: all(f(item) for f in filters)


def get_file_response(api, file_type, file_path, filename, check=True):
    if check and not os.path.exists(file_path):
        api.abort(HTTPStatus.NOT_FOUND, f'{file_type.lower().title()} {filename} not found')
    file = open(file_path, 'rb')
    return send_file(file, attachment_filename=filename, cache_timeout=0)


def get_items_with_relations(all_items, cls, fields=None, relations=None, filters=None):
    def filter_func(item):
        return all(f(item) for f in filters)

    def map_func(item):
        if fields is None:
            result = deepcopy(item)
        else:
            result = dict_copy(item, fields)
        result.update(cls.get_relations(item[cls.__table__.columns.keys()[0]], relations))
        return result

    if filters is None or len(filters) == 0:
        return list(map(map_func, all_items))
    return list(filter(filter_func, list(map(map_func, all_items))))


def get_items_related_to_page(page_id, page_size, all_items):
    start, end = get_page_params(page_id, page_size, len(all_items))
    return all_items[start:end]


def apply_filters_from(filters_data, filters_dict, items):
    filters = get_filters(filters_data, filters_dict)
    if len(filters) > 0:
        return list(filter(lambda item: all([f(item) for f in filters]), items))
    return items


def analyze_update(old_ids, new_ids):
    old_ids = set(old_ids)
    new_ids = set(new_ids)
    add_ids = new_ids.difference(old_ids)
    delete_ids = old_ids.difference(new_ids)
    no_ids = new_ids.intersection(old_ids)
    return add_ids, no_ids, delete_ids


def dict_copy(dictionary: dict, fields: list) -> dict:
    return {field: dictionary[field] for field in fields if field in dictionary}


def dict_update(dictionary: dict, update_dictionary: dict) -> dict:
    dictionary.update(update_dictionary)
    return dictionary


def check_simple_filters(dict_item: dict, filters: dict):
    for key in filters or {}:
        if key in dict_item and dict_item[key] != filters[key]:
            return False
    return True


def check_file(api, file, types, max_length, max_length_mb):
    if os.path.splitext(file.name)[1][1:] in types:
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0, os.SEEK_SET)
        if file_length > max_length:
            # api.abort(HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            #           f'The size of file "{file.filename}" is more than {max_length_mb} MB.')
            return False
    else:
        # api.abort(HTTPStatus.BAD_REQUEST, f'The type of file "{file.filename}" is not supported')
        return False
    return True


def get_item(api, item_id, cls):
    item = cls.get_item_by_id(item_id)
    if item is None:
        api.abort(HTTPStatus.NOT_FOUND, f'{cls.__name__} {item_id} not found')
    return item


def mean(arr):
    arr = list(arr)
    if len(arr) == 0:
        return 0
    return stat_mean(arr)


def hmac_sha1(key, message):
    key = bytes(key, 'UTF-8')
    message = bytes(message, 'UTF-8')
    return base64.b64encode(hmac.new(key, message, sha1).digest()).decode('UTF-8')


def encode_sha1(message):
    return sha1(message.encode('utf-8')).hexdigest()


def check_decoded_message(user_id, encoded):
    encoded_check = encode_sha1(f"{user_id}-{current_app.config['SECRET_KEY_DECODE']}")
    return encoded_check == encoded


def get_bot_start_link(user_id):
    encoded = encode_sha1(f"{user_id}-{current_app.config['SECRET_KEY_DECODE']}")
    return f"{current_app.config['BOT_START_LINK']}{user_id}_{encoded}"


def get_data_frame_from_query(query):
    compiled = query.statement.compile(query.session.bind)
    return pd.read_sql(compiled.string, query.session.bind, params=compiled.params)


def get_data_frame_from_query_string(query, params=None):
    from app.model.db import db

    return pd.read_sql(query, db.session.bind, params=params)


def format_phone(phone_str):
    return re.search(r'\d+', phone_str).group()


def generate_random_email(name, surname):
    return f"{name}_{surname}_{uuid.uuid4().hex[:6].upper()}@Diploma.com"


def generate_random_password():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def get_filters_dict(filters_data, filters_dict):
    filters = {}
    for f in filters_data:
        if f in filters_dict:
            filters[f] = filters_dict[f]
    return filters


def filter_by(cls, **kwargs):
    def f(query):
        for k in kwargs:
            query = query.filter(getattr(cls, k) == kwargs[k])
        return query

    return f


def is_hex_color(data):
    return re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', data)
