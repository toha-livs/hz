import json

import falcon

from auth.resources import Resource
from auth.utils import get_request_multiple, delete_request, get_request_single
from gusto_api.models import Groups


class GroupsResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_multiple(Groups, req.params, resp)

    def on_post(self, req, resp, **kwargs):
        post_data = req.stream.read()
        if post_data:
            post_data = json.loads(post_data)
        else:
            post_data = {}
        try:
            group = Groups(**post_data)

            if group:
                group.save()
                resp.status = falcon.HTTP_201
            else:
                resp.status = falcon.HTTP_400
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400
    # TODO: ask TL about validation data request, should I check this data, or not ?


class GroupResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_single(Groups, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_404
                return
            group = Groups.objects.filter(**kwargs).first()
            if not group:
                resp.status = falcon.HTTP_400
                return
            update_data = json.load(req.stream)
            group.update(**update_data)
            if group:
                group.save()
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_400
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400

    def on_delete(self, req, resp, **kwargs):
        delete_request(Groups, resp, **kwargs)
