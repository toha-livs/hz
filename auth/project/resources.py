import json

import falcon
from falcon_core.resources import Resource

from gusto_api.models import Projects, Groups
from auth.utils import get_request_single, delete_request


class ProjectResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_single(Groups, resp, **kwargs)

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

    def on_put(self, req, resp, **kwargs):
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_404
                return
            project = Projects.objects.filter(**kwargs).first()
            if not project:
                resp.status = falcon.HTTP_400
                return
            update_data = json.loads(req.stream.read())
            project.update(**update_data)
            if project:
                project.save()
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_400

        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400

    def on_delete(self, req, resp, **kwargs):
        delete_request(Projects, resp, **kwargs)
