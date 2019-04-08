from typing import Union, List, Type
from datetime import datetime
from json.decoder import JSONDecodeError

import falcon

from mongoengine import Q

from gusto_api.utils import encrypt
from gusto_api.models import Groups, Users, UsersTokens

MODELS_UNION = Union[Type[Users], Type[Groups]]


def get_request_multiple(model, params, resp):
    """
    return all user after apply params
    :param model: Groups or Users
    :param params:
    :param resp:
    :return:
    """
    fields = filter_data(params)
    sort = fields.pop('sort', 'id')
    if sort not in model.fields:
        sort = 'id'
    off_set = int(fields.pop('offset', 0))
    limit = int(fields.pop('limit', 0))
    model_instance = model.objects.filter(**fields).order_by(sort)
    if limit:
        model_instance = model_instance[off_set:off_set + limit]
    response_list = list_obj_to_serialize_format(model_instance, recurs=True)
    resp.media = response_list
    resp.status = falcon.HTTP_200


def get_request_single(model, resp, **kwargs):
    """
    :param model: Groups, Projects or Users
    :param resp:
    :param kwargs:
    :return: model object
    """
    if 'id' in kwargs.keys():
        model_instance = model.objects.filter(**kwargs).first()
    elif 'project_id' in kwargs.keys():
        model_instance = model.objects.filter(project=kwargs['project_id']).first()
    elif 'group_id' in kwargs.keys():
        model_instance = model.objects.filter(id=kwargs['group_id']).first()

        if model_instance is None:
            resp.status = falcon.HTTP_400
            return

        model_instance = model_instance.project
    else:
        resp.status = falcon.HTTP_400
        return

    if model_instance is None:
        resp.status = falcon.HTTP_400
        return

    resp.media = list_obj_to_serialize_format([model_instance], recurs=True)[0]
    resp.status = falcon.HTTP_200


def token_exists(instance) -> bool:
    """
    Checks if given token exists in the database
    :param instance: UsersToken object
    :return: True or False
    """
    instance.token = UsersTokens.objects(token=instance.token).first()

    return bool(instance.token)


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


def post_create_user(request, response: falcon.Response) -> None:
    """
    if user with email or phone is exist return 'user is already present' in body
    else return new user in media
    """
    try:
        data = falcon.json.load(request.stream)
    except JSONDecodeError:
        response.status = falcon.HTTP_400
        return

    if Users.objects.filter((Q(email=data['email']) or (Q(tel=data['tel'])))):
        response.body = 'user is already present'
        response.status = falcon.HTTP_400
        return

    user = Users(**data)

    user.password = encrypt(user.email + user.tel + user.password)

    user.date_created = datetime.now()
    user.last_login = datetime.now()
    user.is_active = True
    user.save()

    generate_user_token(user)
    response.media = user.to_dict()
    response.status = falcon.HTTP_201


def delete_request(model, resp: falcon.Response, **kwargs) -> None:
    """
       Handler fot DELETE requests
           1) Checks if pk(id) is not None
           2) Found object from model by pk(id)
           3) Delete object from the collection

       :param model: MongoEngine model class
       :param resp: id of and element
       :return:
       """
    if 'id' not in kwargs.keys():
        resp.status = falcon.HTTP_404
        return

    model_instance = model.objects.filter(**kwargs).first()
    if not model_instance:
        resp.status = falcon.HTTP_400
        return

    model_instance.delete()

    resp.status = falcon.HTTP_200


def list_obj_to_serialize_format(list_obj: list, recurs=None):
    response_list = []
    for obj in list_obj:
        var_dict = obj.to_dict(table_name=True)
        if recurs:
            if var_dict.get('table_name') == 'users':
                var_dict['groups'] = list_obj_to_serialize_format(obj.groups)
            elif var_dict.get('table_name') == 'groups':
                var_dict['users'] = list_obj_to_serialize_format(obj.users)
        var_dict.pop('table_name', None)
        response_list.append(var_dict)

    return response_list


def filter_data(data):
    """
    convert str -> bool if value = 'true' ot 'false'
    :param data:
    :return:  converted data
    """
    new_data = {}
    for key, value in data.items():
        if value == 'true':
            new_data[key] = True
        elif value == 'false':
            new_data[key] = False
        else:
            new_data[key] = value
    return new_data
