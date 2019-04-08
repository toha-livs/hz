import json
import datetime

import falcon

from auth.resources import Resource
from gusto_api.models import Users, UsersTokens
from gusto_api.utils import encrypt
from auth.utils import generate_user_token, get_request_multiple, delete_request, get_request_single, post_create_user


class UsersResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_multiple(Users, req.params, resp)

    def on_post(self, req, resp, **kwargs):
        post_create_user(req, resp)


class UserResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        get_request_single(Users, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        user = Users.objects.filter(id=kwargs.get('id'))
        if not user:
            resp.status = falcon.HTTP_404
            return
        user = user[0]
        data = json.load(req.stream)
        if data.get('password'):
            resp.status = falcon.HTTP_400('password is not changeable')
            return
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        generate_user_token(user)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, **kwargs):
        delete_request(Users, resp, **kwargs)

    # for url: /users/registration/
    def on_post(self, req, resp, **kwargs):
        post_create_user(req, resp)


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

        user.update(last_login=datetime.datetime.now())

        token = UsersTokens.objects.filter(user=user).first()

        if token is None:
            resp.status = falcon.HTTP_400
            return

        # TODO: use Anton's to_dict instead
        user = json.loads(user.to_json())
        user['token'] = token.token

        resp.media = user
        resp.status = falcon.HTTP_200
