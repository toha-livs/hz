from falcon_core.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Countries, Currencies
import falcon
import json, datetime

from gusto_api.utils import filter_queryset, dict_from_model


class CurrenciesResource(Resource):
    use_token = True

    currency_template = (
        ('name', 'string'),
        ('symbol', 'string'),
        ('code', 'string'),
        ('rate', 'integer'),
        ('rates', 'list'),
        ('last_update', 'float'),
    )

    def on_get(self, req, resp, **kwargs):
        currencies = filter_queryset(Currencies.objects, **req.params)
        resp.media = dict_from_model(currencies, self.currency_template, iterable=True)
        resp.status = falcon.HTTP_200

    def post(self, req, resp, data, **kwargs):
        if data != {}:
            currency = Currencies(**data)
            currency.last_update = datetime.datetime.now()
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
        country = Currencies.objects.filter(**kwargs).first()
        if country is None:
            resp.status = falcon.HTTP_404
        resp.media = dict_from_model(country, CurrenciesResource.currency_template)
        resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, **kwargs):
        delete_request(Currencies, resp, **kwargs)
