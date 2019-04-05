import datetime
import json

import falcon
from .utils import  list_obj_to_serialize_format
from falcon_core.utils import encrypt_sha256_with_secret_key

from auth.resources import Resource
from gusto_api.models import Users, UsersTokens


def generate_user_token(user_obj: Users) -> None:
    """
    Read docstring for generate_users_tokens_by_group_id
    :param user_obj:
    :return:
    """
    user_groups = user_obj.group_values('permissions')
    text = user_obj.email + user_obj.tel + user_obj.password + str(user_groups)
    user_token = user_obj.get_token
    if user_token is None:
        user_token = UsersTokens(user=user_obj, token=encrypt_sha256_with_secret_key(text))
    else:
        user_token.token = encrypt_sha256_with_secret_key(text)
    user_token.save()

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
#
#