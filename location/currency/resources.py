from falcon_core.resources import Resource
from gusto_api.models import  Currencies
import falcon
import datetime

from gusto_api.utils import filter_queryset, dict_from_model


class CurrenciesResource(Resource):
    use_token = True

    currency_template = (
        ('id', 'string'),
        ('name', 'string'),
        ('symbol', 'string'),
        ('code', 'string'),
        ('rate', 'integer'),
        ('rates', 'list'),
        ('get_last_update:last_update', 'float')
    )

    def get(self, req, resp, **kwargs):
        currencies = filter_queryset(Currencies.objects, **req.params)
        resp.media = dict_from_model(currencies, self.currency_template, iterable=True)
        resp.status = falcon.HTTP_200

    def post(self, req, resp, data, **kwargs):
        if data != {}:
            data['last_update'] = datetime.datetime.now()
            currency = Currencies(**data)
            currency.save()
            resp.media = dict_from_model(currency, self.currency_template)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class CurrencyResource(Resource):
    use_token = True
    currency_template = (
        ('id', 'string'),
        ('name', 'string'),
        ('symbol', 'string'),
        ('code', 'string'),
        ('rate', 'integer'),
        ('rates', 'list'),
        ('get_last_update:last_update', 'float')
    )

    def get(self, req, resp, **kwargs):
        country = Currencies.objects.filter(**kwargs).first()
        if country is None:
            resp.status = falcon.HTTP_404
        resp.media = dict_from_model(country, CurrenciesResource.currency_template)
        resp.status = falcon.HTTP_OK

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
        resp.media = dict_from_model(currency, self.currency_template)
        resp.status = falcon.HTTP_200

    def delete(self, req, resp, data, **kwargs):
        if kwargs.get('id'):
            Currencies.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound