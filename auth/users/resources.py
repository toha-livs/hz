import falcon

from falcon_core.resources import Resource
from falcon_core.utils import dict_from_obj

from gusto_api.models import Users
from gusto_api.utils import filter_queryset, dict_from_model

from auth.utils import encrypt_password


class UsersLoginResource(Resource):
    def post(self, req, resp, data, **kwargs):
        if data.get('login') and data.get('password'):
            user = Users.objects.filter(**{
                ('tel', 'email')[int(bool('@' in data['login']))]: data.pop('login')
            }).first()
            if user and user.password == encrypt_password(user, data['password']):
                resp.media = dict_from_obj(user, (
                    ('id', 'string'),
                    ('name', 'string'),
                    ('email', 'string'),
                    ('tel', 'string'),
                    ('last_login', 'string'),
                    ('date_created', 'string'),
                    ('token', 'string'),
                    ('groups', 'objects', (
                        ('name', 'string'),
                        ('permissions', 'objects', (
                            ('id', 'string'),
                            ('get_access:access', 'string'),
                        )),
                    )),
                ))
            else:
                raise falcon.HTTPUnauthorized
        else:
            raise falcon.HTTPBadRequest


class UsersResource(Resource):
    use_token = True

    def get(self, req, resp, **kwargs):
        if kwargs.get('id'):
            users = Users.objects.filter(id=kwargs['id']).first()
        else:
            users = filter_queryset(Users.objects, **req.params)

        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(users, (
            ('id', 'string'),
            ('name', 'string'),
            ('surname', 'string'),
            ('email', 'string'),
            ('tel', 'string'),
            ('groups', 'string'),
        ), iterable=not bool(kwargs.get('id')))

    def post(self, req, resp, data, **kwargs):
        if not kwargs.get('id'):
            pass
        else:
            raise falcon.HTTPNotFound

    def put(self, req, resp, data, **kwargs):
        if kwargs.get('id'):
            pass
        else:
            raise falcon.HTTPNotFound

    def delete(self, req, resp, data, **kwargs):
        if kwargs.get('id'):
            Users.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
