import falcon
from mongoengine.errors import ValidationError
from falcon_core.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Cities
from gusto_api.utils import filter_queryset, dict_from_model


class CitiesResource(Resource):

    use_token = True

    cities_template = (
        ('name', 'string'),
        ('country_code', 'string'),
        ('default', 'boolean'),
        ('active', 'boolean'),
        ('lat', 'integer'),
        ('lng', 'integer'),
        ('number_phone', 'string'),
        ('language', 'object', (
            ('en', 'string'),
            ('ru', 'string'),
            ('uk', 'string'),
        ),),
        ('exist_store', 'boolean'),
    )

    def on_get(self, req, resp, **kwargs):
        cities = filter_queryset(Cities.objects, **req.params)
        resp.media = dict_from_model(cities, self.cities_template, iterable=True)
        resp.status = falcon.HTTP_200

    def post(self, req, resp, data, **kwargs):
        try:
            city = Cities(**data)
            city.save()
            resp.media = dict_from_model(city, CitiesResource.cities_template)
            resp.status = falcon.HTTP_201
        except ValidationError:
            resp.status = falcon.HTTP_400


class CityResource(Resource):

    def on_get(self, req, resp, **kwargs):
        get_request_single(Cities, resp, **kwargs)

    def put(self, req, resp, data, **kwargs):
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