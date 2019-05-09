from falcon_core.resources import Resource
from gusto_api.models import Currencies
import falcon
import datetime

from gusto_api.utils import filter_queryset, dict_from_model


class CurrenciesResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        currencies = filter_queryset(Currencies.objects, **req.params)
        resp.media = dict_from_model(currencies, Currencies.response_template['short'], iterable=True)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, **kwargs):
        data = req.context['data']
        if data != {}:
            data['last_update'] = datetime.datetime.now()
            currency = Currencies(**data)
            currency.save()
            resp.media = dict_from_model(currency, Currencies.response_template['short'])
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class CurrencyResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        country = Currencies.objects.filter(**kwargs).first()
        if country is None:
            resp.status = falcon.HTTP_404
        resp.media = dict_from_model(country, Currencies.response_template['short'])
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, **kwargs):
        data = req.context['data']
        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_400
            return
        currency = Currencies.objects.filter(**kwargs).first()
        if currency is None:
            resp.status = falcon.HTTPNotFound
            return

        data['last_update'] = datetime.datetime.now()
        currency.update(**data)
        resp.media = dict_from_model(currency, Currencies.response_template['short'])
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, **kwargs):
        if kwargs.get('id'):
            Currencies.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
