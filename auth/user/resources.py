import cgi
import json
import datetime
import time

import falcon

from falcon_core.resources import Resource
from gusto_api.models import Users
from gusto_api.utils import encrypt
from auth.utils import delete_request, post_create_user, encrypt_password
from gusto_api.utils import filter_queryset, dict_from_model


class UsersResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET all users
        url: users/
        """

        users = filter_queryset(Users.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(users, UserResource.users_dict_template, iterable=True)

        # get_request_multiple(Users, req.params, resp)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) user
        url: users/
        """
        post_create_user(req, resp)


class UserResource(Resource):

    users_dict_template = (
            ('id', 'string'),
            ('name', 'string'),
            ('email', 'string'),
            ('tel', 'string'),
            ('is_active', 'boolean'),
            ('get_last_login:last_login', 'float'),
            ('get_date_created:date_created', 'float'),
            ('image', 'string'),
            ('groups', 'objects', (
                ('name', 'string'),
                ('permissions', 'objects', (
                    ('id', 'string'),
                    ('get_access:access', 'string'),
                ),),
            ),)
        )

    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET user by id
        url: users/{id}/
        """
        user = Users.objects.filter(id=kwargs['id']).first()
        if user:
            resp.status = falcon.HTTP_OK
            resp.media = dict_from_model(user, self.users_dict_template)
        else:
            resp.status = falcon.HTTP_404

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
            resp.status = falcon.HTTP_404
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
            user.generate_token()
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, **kwargs):
        """
        DELETE user bu id
        url: users/{id}/
        """
        delete_request(Users, resp, **kwargs)


class LoginResource(Resource):

    def post(self, req, resp, data, **kwargs):
        """
        POST(login) user with given (email or telephone) and password and return user token
        url: users/login/
        """

        if data.get('login') and data.get('password'):
            user = Users.objects.filter(**{
                ('tel', 'email')[int(bool('@' in data['login']))]: data.pop('login')
            }).first()
            if user and user.password == encrypt_password(user, data['password']):
                resp.media = dict_from_model(user, UserResource.users_dict_template)
            else:
                raise falcon.HTTPUnauthorized
        else:
            raise falcon.HTTPBadRequest


class RegistrationResource(Resource):

    def on_post(self, request, response, **kwargs):
        try:
            print(json.load(request.stream))
        except json.JSONDecodeError as e:
            print(e)
            print(request.stream)

        response.status = falcon.HTTP_200
        response.media = {'status': 'OK'}
