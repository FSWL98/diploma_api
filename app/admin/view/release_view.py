from flask import current_app, Markup

from .permissions_view import AdminView
from ...model.entity.api_key import ApiKey
from ...model.entity.release import Release


def _format_notify(self, context, model, name):
    url = f'{current_app.config["HOST"]}{current_app.config["URL_PREFIX"]}/release/notify'
    _html = '''
                <form action="{url}" method="POST">
                    <input id="token" name="token" type="hidden" value="{token}">
                    <input id="release_id" name="release_id"  type="hidden" value="{release_id}">
                    <button type='submit'>Уведомить</button>
                </form>
            '''.format(url=url, release_id=model.release_id,
                       token=ApiKey.get_api_key_by_name('notification').get('key')
                       if ApiKey.get_api_key_by_name('notification') is not None else '')

    return Markup(_html)


class ReleaseView(AdminView):
    deletable = True
    column_list = tuple(Release.__table__.columns) + ('notify',)

    column_formatters = {
        'notify': _format_notify
    }
