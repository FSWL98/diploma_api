import os
import re

from base64 import b64decode
from flask import current_app
from werkzeug.datastructures import FileStorage

from . import get_file_response

IMAGE_EXTENSIONS = {
    'jpeg': 'jpeg',
    'png': 'png',
    'svg+xml': 'svg'
}


def decode_base64(base64):
    try:
        return b64decode(base64)
    except:
        return None


def is_correct_base64(base64):
    match = re.match(r'data:image/(jpeg|png|svg\+xml);base64,', base64)
    if match is None:
        return False
    return decode_base64(base64[match.regs[0][1]:]) is not None


def save_base64(base64: str, filename, s3_url_func=None):
    match = re.match(r'data:image/(jpeg|png|svg\+xml);base64,', base64)
    if match is None:
        return None
    full_filename = f'{filename}.{IMAGE_EXTENSIONS[base64[match.regs[1][0]:match.regs[1][1]]]}'
    image = decode_base64(base64[match.regs[0][1]:])
    if image is None:
        return None

    return full_filename


def save_image(image: FileStorage, filename):
    mimetype = image.mimetype
    match = re.match(r'image/(jpeg|png|svg\+xml)', mimetype)
    if match is None:
        return None
    full_filename = f'{filename}.{IMAGE_EXTENSIONS[mimetype[match.regs[1][0]:match.regs[1][1]]]}'
    image.save(full_filename)
    return full_filename


def save_avatar(avatar_base64, item, avatar_field, get_avatar_name_func, *avatar_args):
    if avatar_base64.startswith('https://'):
        setattr(item, avatar_field, avatar_base64)
        item.add()
    else:
        avatar_path = save_base64(avatar_base64, get_avatar_name_func(*avatar_args),
                                  get_avatar_s3_path)
        if avatar_path is not None:
            setattr(item, avatar_field, os.path.basename(avatar_path))
            item.add()


def update_avatar(avatar_base64, item, avatar_field, get_avatar_name_func, *avatar_args):
    if avatar_base64.startswith('https://'):
        setattr(item, avatar_field, avatar_base64)
    else:
        avatar_path = save_base64(avatar_base64, get_avatar_name_func(*avatar_args),
                                  get_avatar_s3_path)
        if avatar_path is not None:
            setattr(item, avatar_field, os.path.basename(avatar_path))


def get_avatar_s3_url(avatar_name):
    if avatar_name is None:
        return None

    return '/'.join([current_app.config['S3_URL'], current_app.config['S3_BUCKET'],
                     current_app.config['AVATARS_PATH'], avatar_name])


def get_avatar_s3_path(avatar_name):
    if avatar_name is None:
        return None
    return '/'.join([current_app.config['S3_BUCKET'], current_app.config['AVATARS_PATH'], avatar_name])


def get_media_path(media_type, media_name):
    return os.path.join(current_app.config[f'{media_type.upper()}S_DIR'], str(media_name))


def get_image_path(image_name):
    return get_media_path('image', image_name)


def get_media_url(media_type, media_name):
    return f'{current_app.config["HOST"]}{current_app.config["URL_PREFIX"]}/user_file/{media_name}'


def get_image_url(image_name):
    return get_media_url('image', image_name)


def get_picture_response(picture_type, api, picture_name):
    return get_file_response(api, picture_type, get_media_path(picture_type, picture_name), picture_name)


def get_image_response(api, image_name):
    return get_picture_response('image', api, image_name)


def delete_picture(picture_type, picture_name):
    picture_path = get_media_path(picture_type, picture_name)
    if os.path.exists(picture_path):
        os.remove(picture_path)
        return picture_path
    return None


def delete_image(image_name):
    return delete_picture('image', image_name)


def delete_avatar(avatar_name):
    if avatar_name is None:
        return None
    return avatar_name
