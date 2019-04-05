import datetime
import hashlib
import json
import os
from importlib import import_module

import falcon

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


class UsersResource(Resource):
    use_token = True

    def on_get(self, request, response, **kwargs):
        # response.media = get_univ_filter(Users, request.params)
        response.status = falcon.HTTP_200

    def on_post(self, request, response, **kwargs):
        data = json.load(request.stream)
        user = Users(**data)
        user.last_login = datetime.datetime.now()
        user.date_created = datetime.datetime.now()
        user.is_active = True
        user.password = encrypt_sha256_with_secret_key(data.get('email') + data.get('tel') + data.get('password'))
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
        for key, value in data.items():
            print(key)
            if key == 'password':
                print('SET_PASSWORD')

            else:
                setattr(user, key, value)
        print(dir(user))
        print(user.password)
        user.password = encrypt_sha256_with_secret_key(user.email + user.tel + user.password if data.get('password') else data['password'])
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