import json
from datetime import datetime

import falcon
from falcon_core.resources import Resource

from gusto_api.models import Users, UsersTokens
from gusto_api.utils import encrypt


class LoginResource(Resource):
    def on_post(self, req, resp, **kwargs):
        try:
            data = json.load(req.stream)
        except json.JSONDecodeError:
            resp.status = falcon.HTTP_400
            return

        if '@' in data.get('login'):
            user = Users.objects.filter(email=data.get('login')).first()
        else:
            user = Users.objects.filter(tel=data.get('login')).first()

        if user is None:
            resp.status = falcon.HTTP_400
            return

        if user.password != encrypt(''.join((user.email, user.tel, data.get('password')))):
            resp.status = falcon.HTTP_400
            return

        user.update(last_login=datetime.now())

        token = UsersTokens.objects.filter(user=user).first()

        if token is None:
            resp.status = falcon.HTTP_400
            return

        # TODO: use Anton's to_dict instead
        user = json.loads(user.to_json())
        user['token'] = token.token

        resp.media = user
        resp.status = falcon.HTTP_200
