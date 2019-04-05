import datetime
import json

import falcon
from .utils import list_obj_to_serialize_format
from falcon_core.utils import encrypt_sha256_with_secret_key

from auth.resources import Resource
from gusto_api.models import Users, UsersTokens
from gusto_api.utils import encrypt
from auth.utils import generate_user_token


def filter_data(data):
    new_data = {}
    for key, value in data.items():
        if value == 'true':
            new_data[key] = True
        elif value == 'false':
            new_data[key] = False
        else:
            new_data[key] = value
    return new_data


class UsersResource(Resource):
    use_token = True

    def on_get(self, request, response, **kwargs):
        fields = filter_data(request.params)
        sort = fields.pop('sort', 'id')
        if sort not in Users.fields:
            sort = 'id'
        off_set = int(fields.pop('offset', 0))
        limit = int(fields.pop('limit', 0))
        users = Users.objects.filter(**fields).order_by(sort)
        if limit:
            users = users[off_set:off_set + limit]
        response_list = list_obj_to_serialize_format(users, recurs=True)
        response.media = response_list
        response.status = falcon.HTTP_200

    def on_post(self, request, response, **kwargs):
        data = json.load(request.stream)
        user = Users(**data)
        user.last_login = datetime.datetime.now()
        user.date_created = datetime.datetime.now()
        user.is_active = True
        user.password = encrypt_sha256_with_secret_key(user.email + user.tel + user.password)
        user.save()
        generate_user_token(user)
        print(dir(user), 'user_dir')
        response.body = user.to_json()
        response.status = falcon.HTTP_201


class UserResource(Resource):
    use_token = True

    def on_get(self, request, response, **kwargs):
        user = Users.objects.filter(id=kwargs.get('user_id'))
        if not user:
            response.status = falcon.HTTP_404
            return
        response.media = user[0].to_dict()
        response.status = falcon.HTTP_200

    def on_put(self, request, response, **kwargs):
        user = Users.objects.filter(id=kwargs.get('user_id'))
        if not user:
            response.status = falcon.HTTP_404
            return
        user = user[0]
        data = json.load(request.stream)
        if data.get('password'):
            response.status = falcon.HTTP_400('password is not changeable')
            return
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        generate_user_token(user)
        response.status = falcon.HTTP_200

    def on_delete(self, request, response, **kwargs):
        user = Users.objects.filter(id=kwargs.get('user_id'))
        if not user:
            response.status = falcon.HTTP_404
            return
        user[0].delete()
        response.status = falcon.HTTP_204


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
