import falcon
from mongoengine.errors import ValidationError
from auth.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Cities


class CitiesResource(Resource):

    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_multiple(Cities, req.params, resp)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, **kwargs):
        try:
            data = req.stream.read()
            if not data:
                resp.status = falcon.HTTP_400
                return
            data = falcon.json.loads(data)

            city = Cities(**data)
            city.save()
            resp.status = falcon.HTTP_201
        except ValidationError:
            resp.status = falcon.HTTP_400


class CityResource(Resource):

    def on_get(self, req, resp, **kwargs):
        get_request_single(Cities, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        city = Cities.objects.filter(**kwargs).first()
        if city is None:
            resp.status = falcon.HTTP_404
            return
        try:
            data = req.stream.read()
            if not data:
                resp.status = falcon.HTTP_400
                return
            data = falcon.json.loads(data)

            city.update(**data)
            resp.status = falcon.HTTP_200
        except ValidationError:
            resp.status = falcon.HTTP_400

    def on_delete(self, request, response, **kwargs):
        delete_request(Cities, response, **kwargs)