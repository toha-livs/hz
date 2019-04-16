from falcon_core.resources import Resource
from auth.utils import get_request_multiple, get_request_single, delete_request
from gusto_api.models import Countries, Currencies
import falcon
import json


class CountriesResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_multiple(Countries, req.params, resp)

    def on_post(self, req, resp, **kwargs):

        try:
            post_data = req.stream.read()

            if post_data:
                post_data = json.loads(post_data)
            else:
                post_data = {}

            country = Countries(**post_data)
            country.save()

            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400


class CountryResource(Resource):

    def on_get(self, req, resp, **kwargs):
        get_request_single(Countries, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_400
                return

            country = Countries.objects.filter(**kwargs).first()

            if country is None:
                resp.status = falcon.HTTP_400
                return

            update_data = json.loads(req.stream.read())

            if update_data.get('currency', False):
                curr = Currencies.objects.filter(id=update_data['currency']).first()
                if curr:
                    update_data['currency'] = curr

            country.update(**update_data)

            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400

    def on_delete(self, req, resp, **kwargs):
        delete_request(Countries, resp, **kwargs)
