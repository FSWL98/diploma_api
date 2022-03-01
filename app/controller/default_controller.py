from flask_restx import Resource

from ..util import get_version
from ..util.dto import DefaultDto


api = DefaultDto.api


@api.route('version')
class VersionApi(Resource):
    @api.doc('get_version', security='api-token')
    @api.response(200, 'Success', DefaultDto.version)
    def get(self):
        """Get current version"""
        return {'version': get_version()}
