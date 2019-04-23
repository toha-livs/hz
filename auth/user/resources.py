import json
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

    def post(self, req, resp, data,**kwargs):
        """
        POST(create) user
        url: users/
        """
        post_create_user(req, resp, data)


class UserResource(Resource):

    users_dict_template = (
            ('id', 'string'),
            ('name', 'string'),
            ('email', 'string'),
            ('tel', 'string'),
            ('is_active', 'boolean'),
            ('get_date_created:date_created', 'integer'),
            ('image', 'string'),
            ('groups', 'objects', (
                ('id', 'string'),
                ('name', 'string'),
                ('project', 'object', (
                    ('id', 'string'),
                    ('name', 'object', (
                        ('en', 'string'),
                        ('ru', 'string'),
                        ('uk', 'string'),
                    ))
                )),
                ('permissions', 'objects', (
                    ('id', 'string'),
                    ('get_access:access', 'string'),
                )),
                ('g_type', 'string'),
                ('is_owner', 'boolean')
            ))
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

    def post(self, req, resp, data, **kwargs):
        """
        POST(create) user via registration
        url: users/registration/
        """
        post_create_user(req, resp, data)

    def put(self, req, resp, data, **kwargs):
        """
        PUT user by id with given data
        url: users/{id}/
        """
        user = Users.objects.filter(id=kwargs.get('id')).first()

        if user is None:
            resp.status = falcon.HTTP_404
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

    def post(self, request, response, data, **kwargs):
        print(data)

        response.status = falcon.HTTP_200
        response.media = {'status': 'OK'}
