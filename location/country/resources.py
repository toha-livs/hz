from falcon_core.resources import Resource
from auth.utils import delete_request
from gusto_api.models import Countries, Currencies
import falcon
import json

from gusto_api.utils import filter_queryset, dict_from_model


class CountriesResource(Resource):
    use_token = True

    def get(self, req, resp, **kwargs):
        countries = filter_queryset(Countries.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(countries, (
            ('id', 'string'),
            ('name', 'string'),
            ('iso2', 'string'),
            ('dial_code', 'string'),
            ('priority', 'integer'),
            ('area_codes', 'list'),
            ('currency', 'object', (
                ('name', 'string'),
                ('symbol', 'string'),
                ('code', 'string'),
                ('rate', 'integer'),
                ('rate', 'integer')
            )),

        ), iterable=True)

    def post(self, req, resp, data, **kwargs):
        if data != {}:
            country = Countries(**data)
            country.save()
            resp.media = dict_from_model(country, (
                ('id', 'string'),
                ('name', 'string'),
                ('iso2', 'string'),
                ('dial_code', 'string'),
                ('priority', 'integer'),
                ('area_codes', 'list'),
                ('currency', 'object', (
                    ('name', 'string'),
                    ('symbol', 'string'),
                    ('code', 'string'),
                    ('rate', 'integer'),
                    ('rate', 'integer')
                )),
            ))
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class CountryResource(Resource):

    def get(self, req, resp, **kwargs):
        country = Countries.objects.filter(id=kwargs['id']).first()
        if country is None:
            resp.status = falcon.HTTPNotFound
        resp.media = dict_from_model(country, (
            ('id', 'string'),
            ('name', 'string'),
            ('iso2', 'string'),
            ('dial_code', 'string'),
            ('priority', 'integer'),
            ('area_codes', 'list'),
            ('currency', 'object', (
                ('name', 'string'),
                ('symbol', 'string'),
                ('code', 'string'),
                ('rate', 'integer'),
                ('rate', 'integer')
            )),
        ))
        resp.status = falcon.HTTP_OK

    def put(self, req, resp, data, **kwargs):
        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_400
            return

        country = Countries.objects.filter(**kwargs).first()

        if country is None:
            resp.status = falcon.HTTPNotFound
            return

        if data.get('currency', False):
            curr = Currencies.objects.filter(id=data['currency']).first()
            if curr:
                data['currency'] = curr

        country.update(**data)
        resp.media = dict_from_model(country, (
            ('id', 'string'),
            ('name', 'string'),
            ('iso2', 'string'),
            ('dial_code', 'string'),
            ('priority', 'integer'),
            ('area_codes', 'list'),
            ('currency', 'object', (
                ('name', 'string'),
                ('symbol', 'string'),
                ('code', 'string'),
                ('rate', 'integer'),
                ('rate', 'integer')
            )),
        ))
        resp.status = falcon.HTTP_OK

    def delete(self, req, resp, data, **kwargs):
        if kwargs.get('id'):
            Countries.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
