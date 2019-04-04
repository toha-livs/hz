from falcon_core.resources import Resource
import falcon
from .models import Groups
from .utils import get_univ_filter

class GroupsResource(Resource):

    def on_get(self, req, resp, **kwargs):
        result = get_univ_filter(Groups, req.params)
        try:
            req.media = result
            req.status = falcon.HTTP_200
        except Exception as e:
            req.status = falcon.HTTP_404