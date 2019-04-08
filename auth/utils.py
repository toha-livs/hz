from typing import Union, List, Type
from datetime import datetime
from json.decoder import JSONDecodeError

import falcon

from gusto_api.utils import encrypt
from gusto_api.models import Groups, Permissions, Users, UsersTokens, Projects

MODELS_UNION = Union[Type[Users], Type[Groups]]


def get_request_multiple(model, params, resp):
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


# def get_request_util(model: MODELS_UNION, pk: int, response: falcon.Response) -> None:
#     """
#     Handler for GET requests.
#         1) Checks if pk(id) is not None
#         2) Found object from model by pk(id)
#         3) request.media = object_dict
#
#     :param model: PostgreSQL model class
#     :param pk: id of and element
#     :param response: falcon response
#     :return:
#     """
#     if pk is None:
#         response.status = falcon.HTTP_404
#         return
#
#     model_instance = model.objects(pk=pk).first()
#     if not model_instance:
#         response.status = falcon.HTTP_404
#         return
#
#     response.status = falcon.HTTP_200
#     response.media = get_serialize_object_to_dict(model_instance)


# def put_request_util(model: MODELS_UNION, data: str, pk: int, response: falcon.Response) -> None:
#     """
#     Handler for PUT requests.
#         1) Checks if pk(id) is not None
#         2) Found object from model by pk(id)
#         3) Tries to convert data into JSON
#         4) Filter only fields that model contains
#         5) Iterate through this fields and check if data is in proper type
#         5) Update this fields with new data
#
#      :param model: PostgreSQL model class
#      :param data: string from request.stream
#      :param pk: id of and element
#      :param response: falcon response
#      :return:
#      """
#     if pk is None:
#         response.status = falcon.HTTP_404
#         return
#
#     model_instance = model.objects(pk=pk).first()
#     if not model_instance:
#         response.status = falcon.HTTP_404
#         return
#
#     try:
#         data = json.load(data)
#     except JSONDecodeError:
#         response.status = falcon.HTTP_400
#         return
#
#     same_fields = data.keys() & model.fields.keys()
#     for field in same_fields:
#         if isinstance(data[field], model.fields[field]):
#             if isinstance(getattr(model_instance, field), datetime):
#                 setattr(model_instance, field, datetime.fromtimestamp(data[field]))
#             else:
#                 setattr(model_instance, field, data[field])
#
#     response.status = falcon.HTTP_200
#     response.media = get_serialize_object_to_dict(model_instance)


def delete_request(model, resp: falcon.Response, **kwargs) -> None:
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
                print(obj)
                print(obj.groups)
                var_dict['groups'] = list_obj_to_serialize_format(obj.groups)
            elif var_dict.get('table_name') == 'groups':
                var_dict['users'] = list_obj_to_serialize_format(obj.users)
        var_dict.pop('table_name', None)
        response_list.append(var_dict)

    return response_list


def get_permissions_group(permissions_ids: List[List[int]]) -> list:
    """
    function get list of permissions_ids, and in cycle get property "get_access"
    :param permissions_ids:
    [[1, 323, 32], [1, 123, 213, 12]]
    :return:
    [{'pk': 12, 'access': 'perm32_w'}, {'pk': 43, 'access': 'perm35_w'},]
    """
    response_list = []
    for permission in Permissions.objects().all():
        response_list.append({'id': permission.pk, 'access': permission.get_access})
    return response_list


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

