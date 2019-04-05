import json
from typing import Union, List, Type
from datetime import datetime
from json.decoder import JSONDecodeError

import falcon

from gusto_api.utils import encrypt
from gusto_api.models import Groups, Permissions, Users, UsersTokens

MODELS_UNION = Union[Type[Users], Type[Groups]]


def token_exists(instance) -> bool:
    """
    Checks if given token exists in the database
    :param instance: UsersToken object
    :return: True or False
    """
    instance.token = UsersTokens.objects(token=instance.token).first()

    return bool(instance.token)


def generate_user_token(user_obj: Users) -> None:
    """
    Read docstring for generate_users_tokens_by_group_id
    :param user_obj:
    :return:
    """
    user_groups = user_obj.groups_values('permissions_ids')
    text = user_obj.email + user_obj.tel + user_obj.password + str(user_groups)
    user_token = user_obj.get_token
    if user_token is None:
        user_token = UsersTokens(user_id=user_obj.pk, token=encrypt(text))
        user_token.save()
    else:
        user_token.token = encrypt(text)
        user_token.reload()  # or save()
    user_token.save()


def generate_users_tokens_by_group_id(group_id: int) -> None:
    """
    Generate user tokens in format:
        login + password + [permissions_ids] + SECRET_KEY
    and update them into UserTokens
    :param group_id: int that represent id in Group model
    :return:
    """
    group = Groups.objects(pk=group_id).first()

    for user in group.users:
        generate_user_token(user)


def post_create_user(data: str, response: falcon.Response) -> None:
    try:
        data = falcon.json.load(data)
    except JSONDecodeError:
        response.status = falcon.HTTP_400
        return

    same_user = Users.objects(Users.email.like(data.get('email'))) | (Users.tel.like(data.get('tel'))).first()
    # same_user = Users.objects(Users.email(data.get('email'))) | (Users.tel(data.get('tel'))).first()

    if same_user:
        if same_user.email == data.get('email'):
            response.body = "This email is already in use"
        else:
            response.body = "This tel is already use"
        response.status = falcon.HTTP_400
        return

    model_instance = Users()
    same_fields = data.keys() & Users.fields.keys()
    for field in same_fields:
        if isinstance(data[field], Users.fields[field]):
            if field == 'password':
                setattr(model_instance, field, encrypt(data.get('email') + data.get('tel') + data[field]))
            else:
                setattr(model_instance, field, data[field])
    model_instance.date_created = datetime.now()
    model_instance.last_login = datetime.now()
    model_instance.is_active = True

    model_instance.save()
    generate_user_token(model_instance)
    response.status = falcon.HTTP_201


def get_request_util(model: MODELS_UNION, pk: int, response: falcon.Response) -> None:
    """
    Handler for GET requests.
        1) Checks if pk(id) is not None
        2) Found object from model by pk(id)
        3) request.media = object_dict

    :param model: PostgreSQL model class
    :param pk: id of and element
    :param response: falcon response
    :return:
    """
    if pk is None:
        response.status = falcon.HTTP_404
        return

    model_instance = model.objects(pk=pk).first()
    if not model_instance:
        response.status = falcon.HTTP_404
        return

    response.status = falcon.HTTP_200
    response.media = get_serialize_object_to_dict(model_instance)


def put_request_util(model: MODELS_UNION, data: str, pk: int, response: falcon.Response) -> None:
    """
    Handler for PUT requests.
        1) Checks if pk(id) is not None
        2) Found object from model by pk(id)
        3) Tries to convert data into JSON
        4) Filter only fields that model contains
        5) Iterate through this fields and check if data is in proper type
        5) Update this fields with new data

     :param model: PostgreSQL model class
     :param data: string from request.stream
     :param pk: id of and element
     :param response: falcon response
     :return:
     """
    if pk is None:
        response.status = falcon.HTTP_404
        return

    model_instance = model.objects(pk=pk).first()
    if not model_instance:
        response.status = falcon.HTTP_404
        return

    try:
        data = json.load(data)
    except JSONDecodeError:
        response.status = falcon.HTTP_400
        return

    same_fields = data.keys() & model.fields.keys()
    for field in same_fields:
        if isinstance(data[field], model.fields[field]):
            if isinstance(getattr(model_instance, field), datetime):
                setattr(model_instance, field, datetime.fromtimestamp(data[field]))
            else:
                setattr(model_instance, field, data[field])

    response.status = falcon.HTTP_200
    response.media = get_serialize_object_to_dict(model_instance)


def delete_request_util(model: MODELS_UNION, pk: int, response: falcon.Response) -> None:
    """
    Handler fot DELETE requests
        1) Checks if pk(id) is not None
        2) Found object from model by pk(id)
        3) Delete object from the table

    :param model: PostgreSQL model class
    :param pk: id of and element
    :param response: falcon response
    :return:
    """
    if pk is None:
        response.status = falcon.HTTP_404
        return

    model_instance = model.objects(pk=pk).first()
    if not model_instance:
        response.status = falcon.HTTP_404
        return

    response.media = get_serialize_object_to_dict(model_instance)
    model_instance.delete()
    model_instance.save()


def get_serialize_object_to_dict_2(var_obj: MODELS_UNION) -> dict:
    """
    function get object of class <Users>, filtering datetime and reserved property,
    return dict
    :param var_obj:
     None
    :return:
    {'author': 'anton'}
    """

    response_dict = {}
    user_dict = vars(var_obj)
    for key, value in user_dict.items():
        if isinstance(value, datetime):
            value = value.timestamp()
        response_dict[key] = value
    response_dict.pop('_sa_instance_state')
    if response_dict.get('password'):
        response_dict.pop('password')
    return response_dict


def get_serialize_object_to_dict(var_obj: MODELS_UNION) -> dict:
    """
    function get object of class <Users>, filtering datetime and reserved property,
    return dict
    :param var_obj:
     None
    :return:
    {'author': 'anton'}
    """

    DISABLED_KEYS = [
        '_sa_instance_state', 'password', 'users_ids', 'groups_ids'
    ]

    response_dict = {}
    user_dict = vars(var_obj)
    for key, value in user_dict.items():
        if isinstance(value, datetime):
            value = value.timestamp()
        response_dict[key] = value
    [response_dict.pop(key, None) for key in DISABLED_KEYS]
    response_dict['id'] = response_dict.pop('pk')

    return response_dict


def get_permissions_group(permissions_ids: List[List[int]]) -> list:
    """
    function get list of permissions_ids, and in cycle get property "get_access"
    :param permissions_ids:
    [[1, 323, 32], [1, 123, 213, 12]]
    :return:
    [{'pk': 12, 'access': 'perm32_w'}, {'pk': 43, 'access': 'perm35_w'},]
    """
    response_list = []
    # session.query(Permissions).filter(Permissions.pk.in_(permissions_ids)).all()
    for permission in Permissions.objects(  ).all():
        response_list.append({'id': permission.pk, 'access': permission.get_access})
    return response_list


def get_serialize_obj_list(var_obj_list: list, deep_recurs: int) -> list:
    """
    function get list of objects class <Groups>, filtering reserved property,
    :param var_obj_list:
    [class <Groups>, class <Groups>]
    :param deep_recurs:
    :return:
    [{'pk': 12, 'name': 'hz'}, {'pk': 52, 'name': 'hz2'}]
    """
    response_list = []
    for var_obj in var_obj_list:

        var_dict = get_serialize_object_to_dict(var_obj)
        if getattr(var_obj, 'permissions', False):
            var_dict['permissions'] = get_permissions_group(var_dict['permissions_ids'])
            var_dict.pop('permissions_ids', None)
        for field in getattr(var_obj, 'temp_fields', []):
            if getattr(var_obj, field, False) and deep_recurs != 0:
                var_dict[field] = get_serialize_obj_list(getattr(var_obj, field), deep_recurs=deep_recurs - 1)
        response_list.append(var_dict)

    return response_list


def groups_with_info_users(session, groups=None) -> Union[list, None]:
    def del_privat_method(obj: MODELS_UNION) -> dict:
        return {k: v for k, v in vars(obj).items() if '_' != str(k)[0]}

    def filter_data(data) -> list:
        res_data = []
        for i in data:
            res = {}
            for k, v in i.items():

                if isinstance(v, datetime):
                    res[k] = datetime.timestamp(v)
                elif k == 'password':
                    continue
                elif k == 'pk':
                    res['id'] = v
                else:
                    res[k] = v
            res_data.append(res)
        return res_data

    def get_permissions_info(obj) -> dict:
        return {'id': obj.pk, 'info': obj.get_access}

    try:
        if groups is None:
            groups = Groups.objects.all()
        get_data = []
        for group in groups:
            group_column_filtered = del_privat_method(group)
            group_column_filtered['id'] = group_column_filtered['pk']
            del group_column_filtered['users_ids']
            del group_column_filtered['permissions_ids']
            del group_column_filtered['pk']
            group_column_filtered['users'] = filter_data(list(map(lambda obj: del_privat_method(obj), group.users)))
            group_column_filtered['permissions'] = list(map(lambda obj: get_permissions_info(obj), group.permissions))
            get_data.append(group_column_filtered)
        return get_data
    except Exception as e:
        print(e)


def get_univ_filter(model_obj: MODELS_UNION, params: dict) -> list:
    sort = params.get('sort', 'id')
    if sort not in model_obj.fields:
        sort = 'id'
    elif sort == 'g_type':
        sort = 'type'
    off_set = int(params.get('offset', 0))
    limit = int(params.get('limit', 0))
    reqursions_step = int(params.get('recur', 1))
    same_fields = params.keys() ^ model_obj.fields.keys()
    [params.pop(key, None) for key in ['sort', 'off_set', 'limit'] + list(same_fields)]
    query_list = model_obj.objects.filter(**params).order_by(sort)
    # query_list = session.query(model_obj).filter_by(**params).order_by(sort)

    if limit:
        var_list = query_list.slice(off_set, off_set + limit).all()
    else:
        count = model_obj.objects.count()
        var_list = query_list.slice(off_set, count).all()

    var_list = get_serialize_obj_list(var_list, deep_recurs=reqursions_step)

    return var_list
