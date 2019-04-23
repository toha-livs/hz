from falcon_core.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Countries, Currencies
import falcon
import json, datetime

from gusto_api.utils import dict_from_model


class CurrenciesResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_multiple(Currencies, req.params, resp)

    def post(self, req, resp, data, **kwargs):
        if data != {}:
            data['last_update'] = datetime.datetime.now()
            currency = Currencies(**data)
            currency.save()
            resp.media = dict_from_model(currency, (
                ('id', 'string'),
                ('name', 'string'),
                ('code', 'string'),
                ('rate', 'integer'),
                ('rates', 'list'),
                ('get_last_update:last_update', 'float')
            ))
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class CurrencyResource(Resource):

    def on_get(self, req, resp, **kwargs):
        get_request_single(Currencies, resp, **kwargs)

    def put(self, req, resp, data, **kwargs):
        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_400
            return
        currency = Currencies.objects.filter(**kwargs).first()
        if currency is None:
            resp.status = falcon.HTTPNotFound
            return

        data['last_update'] = datetime.datetime.now()
        currency.update(**data)
        resp.media = dict_from_model(currency, (
            ('id', 'string'),
            ('name', 'string'),
            ('code', 'string'),
            ('rate', 'integer'),
            ('rates', 'list'),
            ('get_last_update:last_update', 'float')
        ))
        resp.status = falcon.HTTP_200

    def delete(self, req, resp, data, **kwargs):
        if kwargs.get('id'):
            Currencies.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
