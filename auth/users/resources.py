import falcon

from falcon_core.resources import Resource

from mongoengine import QuerySet

from gusto_api.models import Users
from falcon_core.utils import DictGenerator, register_iterable, dict_from_obj

from auth.utils import encrypt_password


register_iterable(DictGenerator, QuerySet)


class UsersLoginResource(Resource):
    def post(self, req, resp, data, **kwargs):
        if data.get('login') and data.get('password'):
            user = Users.objects.filter(**{
                ('tel', 'email')[int('@' in data['login'])]: data.pop('login')
            }).first()
            if user and user.password == encrypt_password(user, data['password']):
                resp.media = dict_from_obj(user, (
                    ('name', 'string'),
                ))
            else:
                raise falcon.HTTPUnauthorized
        else:
            raise falcon.HTTPBadRequest
