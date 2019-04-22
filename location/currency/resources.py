from falcon_core.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Countries, Currencies
import falcon
import json, datetime


class CurrenciesResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_multiple(Currencies, req.params, resp)

    def on_post(self, req, resp, **kwargs):

        try:
            post_data = req.stream.read()

            if post_data:
                post_data = json.loads(post_data)
            else:
                post_data = {}
            post_data['last_update'] = datetime.datetime.now()
            country = Currencies(**post_data)
            country.save()

            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400


class CurrencyResource(Resource):

    def on_get(self, req, resp, **kwargs):
        get_request_single(Currencies, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_400
                return

            country = Currencies.objects.filter(**kwargs).first()

            if country is None:
                resp.status = falcon.HTTP_400
                return

            update_data = json.loads(req.stream.read())
            update_data['last_update'] = datetime.datetime.now()
            country.update(**update_data)
            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            print('qweqweqwqweqweqweqweqewqweeqw')
            resp.status = falcon.HTTP_400

    def on_delete(self, req, resp, **kwargs):
        delete_request(Currencies, resp, **kwargs)
