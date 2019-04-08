import json

import falcon

from auth.resources import Resource
from auth.utils import delete_request
from gusto_api.models import Projects


class ProjectResource(Resource):

    use_token = True

    def on_post(self, req, resp, **kwargs):
        data = json.load(req.stream)
        if not data:
            resp.status = falcon.HTTP_400
            return
        try:
            new_project = Projects(**data)
            new_project.save()
        except:
            resp.body = 'Error on commit.'
            resp.status = falcon.HTTP_400
            return
        resp.media = new_project.to_dict()
        resp.status = falcon.HTTP_201

    def on_delete(self, req, resp, **kwargs):
        delete_request(Projects, resp, **kwargs)

