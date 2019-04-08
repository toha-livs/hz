from falcon_core.resources import Resource

from gusto_api.models import Projects, Groups

from auth.utils import get_request_single


class ProjectResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_single(Groups, resp, **kwargs)
