import json
from json import JSONDecodeError
from datetime import datetime

import falcon

from gusto_api.utils import encrypt
from gusto_api.models import *


def generate_user_token(user):
    user_permissions = user.groups_values('permissions').all()
    permissions_ids = [x.id for y in user_permissions for x in y]

    text = ''.join((user.email, user.tel, user.password, str(permissions_ids)))

    user_token = user.get_token
    if user_token is None:
        user_token = UsersTokens(user=user, token=encrypt(text))
        user_token.save()
    else:
        user_token.update(token=encrypt(text))


def generate_users_tokens_by_group(group):
    for user in group.users:
        generate_user_token(user)


def delete_request_util(model, pk: str, response: falcon.Response) -> None:
    """
       Handler fot DELETE requests
           1) Checks if pk(id) is not None
           2) Found object from model by pk(id)
           3) Delete object from the collection

       :param model: MongoEngine model class
       :param pk: id of and element
       :param response: falcon response
       :return:
       """
    if pk is None:
        response.status = falcon.HTTP_400
        return

    model_instance = model.objects.filter(id=pk).first()
    if model_instance is None:
        response.status = falcon.HTTP_400
        return

    model_instance_dict = json.loads(model_instance.to_json())
    for key, value in model_instance_dict.items():
        if isinstance(value, list):
            for index, item in enumerate(value):
                model_instance_dict[key][index] = json.loads(getattr(model_instance, key)[index].to_json())
    response.media = model_instance_dict
    model_instance.delete()
