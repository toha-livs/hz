from falcon_core.resources import Resource
from gusto_api.models import Countries, Currencies
import falcon

from gusto_api.utils import filter_queryset, dict_from_model


class CountriesResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        countries = filter_queryset(Countries.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(countries, Countries.response_template['short'], iterable=True)

    def on_post(self, req, resp, **kwargs):
        data = req.context['data']
        if data != {}:
            country = Countries(**data)
            country.save()
            resp.media = dict_from_model(country, Countries.response_template['short'])
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class CountryResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        country = Countries.objects.filter(id=kwargs['id']).first()
        if country is None:
            resp.status = falcon.HTTPNotFound
        resp.media = dict_from_model(country, Countries.response_template['short'])
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, **kwargs):
        data = req.context['data']
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
        resp.media = dict_from_model(country, Countries.response_template['short'])
        resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, **kwargs):
        if kwargs.get('id'):
            Countries.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
