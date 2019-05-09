import falcon
from mongoengine.errors import ValidationError
from falcon_core.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Cities
from gusto_api.utils import filter_queryset, dict_from_model


class CitiesResource(Resource):

    use_token = True

    def on_get(self, req, resp, **kwargs):
        cities = filter_queryset(Cities.objects, **req.params)
        resp.media = dict_from_model(cities, Cities.response_templates['short'], iterable=True)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, **kwargs):
        data = req.context['data']
        try:
            city = Cities(**data)
            city.save()
            resp.media = dict_from_model(city, Cities.response_templates['short'])
            resp.status = falcon.HTTP_201
        except ValidationError:
            resp.status = falcon.HTTP_400


class CityResource(Resource):

    def on_get(self, req, resp, **kwargs):
        city = Cities.objects.filter(id=kwargs['id']).first()
        if city:
            resp.status = falcon.HTTP_OK
            resp.media = dict_from_model(city, Cities.response_templates['short'])
        else:
            resp.status = falcon.HTTP_404

    def on_put(self, req, resp, **kwargs):
        data = req.context['data']
        city = Cities.objects.filter(**kwargs).first()
        if city is None:
            resp.status = falcon.HTTP_404
            return
        try:
            city.update(**data)
            resp.status = falcon.HTTP_200
        except ValidationError:
            resp.status = falcon.HTTP_400

    def on_delete(self, request, response, **kwargs):
        delete_request(Cities, response, **kwargs)