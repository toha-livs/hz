import time
import random

import falcon

from falcon_core.resources import Resource, JSONResource

from gusto_api.models import SMS


class SMSResource(Resource):
    use_token = False

    def on_post(self, req, resp, **kwargs):
        data = req.context['data']
        if data != {}:

            code = str(random.randint(1000, 9999))

            sms = SMS(tel=data.get('tel', None), code=code)
            timestamp = time.time()
            sms.created = timestamp
            sms.expire = timestamp + 300
            sms.save()
            resp.media = {'code': code}
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class SMSCheckResource(Resource):
    use_token = False

    def on_post(self, req, resp, **kwargs):
        data = req.context['data']
        if data != {}:
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
        else:
            resp.status = falcon.HTTP_BAD_REQUEST
