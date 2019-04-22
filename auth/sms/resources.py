import json
import time
import random

import falcon

from falcon_core.resources import Resource

from gusto_api.models import SMS


class SMSResource(Resource):
    def on_post(self, req, resp, **kwargs):
        try:
            data = json.load(req.stream)
        except json.JSONDecodeError as e:
            print(e)
            resp.status = falcon.HTTP_400
            return
        code = str(random.randint(1000, 9999))

        sms = SMS(tel=data.get('tel', None), code=code)
        timestamp = time.time()
        sms.created = timestamp
        sms.expire = timestamp + 300
        sms.save()
        resp.media = {'code': code}
        resp.status = falcon.HTTP_200


class SMSCheckResource(Resource):
    def on_post(self, req, resp, **kwargs):
        try:
            data = json.load(req.stream)
        except json.JSONDecodeError as e:
            print(e)
            resp.body = "can't convert data in json"
            resp.status = falcon.HTTP_400
            return
        sms = SMS.objects.filter(**data).first()
        if sms is None:
            resp.body = 'No instance with such data'
            resp.status = falcon.HTTP_400
            return

        if sms.expire < time.time():
            resp.body = 'Code has been expired'
            resp.status = falcon.HTTP_400
            return

        resp.status = falcon.HTTP_200
        resp.media = {'status': 'OK'}
