import json
import datetime
import time

import falcon

from auth.resources import Resource
from gusto_api.models import Users, UsersTokens
from gusto_api.utils import encrypt
from auth.utils import generate_user_token, get_request_multiple, delete_request, get_request_single, post_create_user, \
    list_obj_to_serialize_format


class UsersResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET all users
        url: users/
        """
        get_request_multiple(Users, req.params, resp)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) user
        url: users/
        """
        post_create_user(req, resp)


class UserResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET user by id
        url: users/{id}/
        """
        get_request_single(Users, resp, **kwargs)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) user via registration
        url: users/registration/
        """
        post_create_user(req, resp)

    def on_put(self, req, resp, **kwargs):
        """
        PUT user by id with given data
        url: users/{id}/
        """
        user = Users.objects.filter(id=kwargs.get('id')).first()

        if user is None:
            resp.status = falcon.HTTP_400
            return

        try:
            data = json.load(req.stream)
        except json.JSONDecodeError:
            resp.status = falcon.HTTP_400
            return

        if not data.get('password'):
            data.pop('password', None)
        else:
            data['password'] = encrypt(user.email + user.tel + data['password'])

        if not data.get('last_login'):
            data.pop('last_login', None)

        same_fields = {x: data[x] for x in user.fields & data.keys()}
        if same_fields:
            user.update(**same_fields)
            generate_user_token(user)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, **kwargs):
        """
        DELETE user bu id
        url: users/{id}/
        """
        delete_request(Users, resp, **kwargs)


class LoginResource(Resource):

    def on_post(self, req, resp, **kwargs):
        """
        POST(login) user with given (email or telephone) and password and return user token
        url: users/login/
        """
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

        user = list_obj_to_serialize_format([user], recurs=True)[0]
        user['token'] = token.token
        print(user)
        resp.media = user
        resp.status = falcon.HTTP_200


class RegistrationResource(Resource):

    def on_post(self, request, response, **kwargs):
        try:
            print(json.load(request.stream))
        except json.JSONDecodeError as e:
            print(e)
            print(request.stream)

        response.status = falcon.HTTP_200
        response.media = {'status': 'OK'}
