import cgi
import json

from typing import Union, List, Type
from datetime import datetime
from json.decoder import JSONDecodeError

from falcon_core.utils import encrypt_sha256_with_secret_key
from falcon_core.config import settings

import falcon
import unidecode
import requests

from mongoengine import Q

from gusto_api.utils import encrypt, dict_from_model
from gusto_api.models import Groups, Users, UsersTokens, Projects, Currencies, Countries, Cities

MODELS_UNION = Union[Type[Users], Type[Groups], Type[Projects], Type[Currencies], Type[Countries], Type[Cities]]


def get_request_multiple(model: MODELS_UNION, params: dict, resp: falcon.Response) -> None:
    """
    Util for HTTP GET request. Gives LIST of model instances to the front-end
    :param model: class inherited from MongoEngine Document
    :param params: dict of params
    :param resp: falcon Response
    """
    fields = filter_data(params)
    sort = fields.pop('sort', 'id')

    if sort not in model.fields:
        sort = 'id'

    off_set = int(fields.pop('offset', 0))
    limit = int(fields.pop('limit', 0))

    same_fields = {x: fields[x] for x in model.fields & fields.keys()}

    model_instance = model.objects.filter(**same_fields).order_by(sort)

    if limit:
        model_instance = model_instance[off_set:off_set + limit]
    else:
        model_instance = model_instance[off_set:]

    response_list = list_obj_to_serialize_format(model_instance, recurs=True)
    resp.media = response_list
    resp.status = falcon.HTTP_200


def get_request_single(model: MODELS_UNION, resp: falcon.Response, **kwargs) -> None:
    """
    Util for HTTP GET request. Gives ONE model object to the front-end
    :param model: class inherited from MongoEngine Document
    :param resp: falcon Response
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


def token_exists(instance: UsersTokens) -> bool:
    """
    Checks if given token exists in the database
    :param instance: UsersToken object
    :return: True or False
    """
    instance.token = UsersTokens.objects(token=instance.token).first()

    return bool(instance.token)


def generate_user_token(user: Users) -> None:
    """
    Generates user token by this formula:
        email + tel + password + list(permissions_ids) + secret_key
    and encrypt it with sha256
    :param user: instance of the Users class inharited from MongoEngine Document class
    """
    user_permissions = user.groups_values('permissions').all()
    permissions_ids = [x.id for y in user_permissions for x in y]

    text = ''.join((user.email, user.tel, user.password, str(permissions_ids)))

    user_token = user.get_token
    if user_token is None:
        user_token = UsersTokens(user=user, token=encrypt(text))
        user_token.save()
    else:
        user_token.update(token=encrypt(text))


def generate_users_tokens_by_group(group: Groups):
    """
    Iterate through users subscribed to given group and generate for them token
    :param group: instance of the Group class inherited from MongoEngine Document class
    """
    for user in group.users:
        generate_user_token(user)


def post_create_user(req: falcon.Request, resp: falcon.Response, data) -> object:
    """
    Create user. Handler for HTTP POST request on users/login/ and /users/
    :param req: instance of falcon.Request class
    :param resp: instance of falcon.Response class
    """

    if Users.objects.filter((Q(email=data['email']) or (Q(tel=data['tel'])))):
        resp.status = falcon.HTTP_400
        resp.body = 'user is already present'
        return

    images = data.pop('images', None)

    user = Users(**data)
    user.password = encrypt(user.email + user.tel + user.password)

    user.date_created = datetime.now()
    user.last_login = datetime.now()
    user.is_active = True
    user.save()
    user.generate_token()
    # generate_user_token(user)
    return user


# NEW!!!!!
# def post_create_user(req: falcon.Request, resp: falcon.Response) -> None:
#     """
#     Create user. Handler for HTTP POST request on users/login/ and /users/
#     :param req: instance of falcon.Request class
#     :param resp: instance of falcon.Response class
#     """
#     data = cgi.FieldStorage(fp=req.stream, environ=req.env)
#
#     if Users.objects.filter((Q(email=data['email'].value) or (Q(tel=data['tel'].value)))):
#         resp.status = falcon.HTTP_400
#         resp.body = 'user is already present'
#         return
#
#     data_keys = data.keys()
#     data_keys.remove('images')
#     new_d = {x: data[x].value for x in data_keys}
#     user = Users(**new_d)
#
#     user.password = encrypt(user.email + user.tel + user.password)
#
#     user.date_created = datetime.now()
#     user.last_login = datetime.now()
#     user.is_active = True
#     try:
#         images = json.loads(send_files_to_file_server(data['images'], resp, 'images', 'images/'))
#     except json.JSONDecodeError as e:
#         print(e)
#         images = {}
#
#     user.image = req.forwarded_prefix + "/" + images.get('image', '')
#     # user.save()
#     # generate_user_token(user)
#     resp.media = user.to_dict()
#     resp.status = falcon.HTTP_201


def delete_request(model: MODELS_UNION, resp: falcon.Response, **kwargs) -> None:
    """
       Handler fot DELETE requests
           1) Checks if pk(id) is not None
           2) Found object from model by pk(id)
           3) Delete object from the collection

       :param model: MongoEngine model class
       :param resp: id of and element
       """
    if 'id' not in kwargs.keys():
        resp.status = falcon.HTTP_400
        return

    model_instance = model.objects.filter(**kwargs).first()
    if model_instance is None:
        resp.status = falcon.HTTP_400
        return

    model_instance.delete()

    resp.status = falcon.HTTP_204


def list_obj_to_serialize_format(list_obj: list, recurs: bool = False) -> List[dict]:
    """
    Convert objects to dict representation
    :param list_obj: list of model instances
    :param recurs: need for ListFields in models
    """
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


def filter_data(data: dict) -> dict:
    """
    Get params from HTTP request and change 'true' or 'false' with python's True or False
    :param data: dict
    :return: dict
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


# def send_files_to_file_server(data, response: falcon.Response, field=None, url=None) -> None:
#     """
#     Sends files to a specific route of the file-server depending on a file type
#     """
#
#     # urls = {
#     #     'images': 'images/',
#     #     'videos': 'videos/',
#     #     'files': 'files/'
#     # }
#
#     form = cgi.FieldStorage(fp=request.stream, environ=request.env)
#
#     if form.getvalue(field):
#         if isinstance(form[field], list):
#             files = [(field, (unidecode.unidecode(x.filename), x.file)) for x in form[field]]
#         else:
#             files = [(field, (unidecode.unidecode(form[field].filename), form[field].file))]
#
#         rp = requests.post(settings.FILE_SERVER_URL + url, files=files)
#         if rp.status_code != 200:
#             response.status = falcon.HTTP_400
#             return
#         response.status = str(rp.status_code)
#         return rp.text

# NEW!!!!!
def send_files_to_file_server(files, response: falcon.Response, field=None, url=None) -> None:
    """
    Sends files to a specific route of the file-server depending on a file type
    """

    # urls = {
    #     'images': 'images/',
    #     'videos': 'videos/',
    #     'files': 'files/'
    # }

    if isinstance(files, list):
        files = [(field, (unidecode.unidecode(x.filename), x.file)) for x in files]
    else:
        files = [(field, (unidecode.unidecode(files.filename), files.file))]

    rp = requests.post(settings.FILE_SERVER_URL + url, files=files)
    if rp.status_code != 200:
        response.status = falcon.HTTP_400
        return
    response.status = str(rp.status_code)
    return rp.text


def encrypt_password(user, password):
    return encrypt_sha256_with_secret_key(user.email + user.tel + password)


def get_user_token(token):
    return UsersTokens.objects.filter(token=token).first()


######################################### test

#
# def f_str(value):
#     return str(value)
#
#
# def f_int(value):
#     if isinstance(value, datetime):
#         value = datetime.timestamp(value)
#     return int(value)
#
#
# def f_float(value):
#     if isinstance(value, datetime):
#         value = datetime.timestamp(value)
#     return float(value)
#
#
# def f_bool(value):
#     return bool(value)
#
#
# def obj_to_dict(obj, template):
#     resp_dict = {}
#     for attr, rule, *t in template:
#         rule = rules.get(rule)
#         if t:
#             resp_dict[attr] = rule(getattr(obj, attr), t)
#         else:
#             resp_dict[attr] = rule(getattr(obj, attr))
#
#         # if attr[:6] == 'object':
#         #     dic = {atr[0]: pars(getattr(obj, atr[0]), atr[2], iterable=True if atr[1][-1] is 's' else False)}
#         #     print(dic)
#         #     resp_dict.update(dic)
#         # else:
#         # dic = {atr[0]: eval(rules[atr[1]])(getattr(obj, atr[0]))}
#         # print(dic)
#         # resp_dict.update(dic)
#     # print(resp_dict)
#     return resp_dict
#
#
# def objs_to_dict(obj, template):
#     return [obj_to_dict(o, template) for o in obj]
#
#
# def execute_rule(obj, rule, template=None):
#     rule = rules.get(rule)
#     if rule:
#         return rule(obj, *template)
#     return None
#
#
# def pars(query, template: tuple, iterable=False):
#     # if iterable:
#     #     return [obj_to_dict(obj, template) for obj in query]
#     # else:
#     #     return obj_to_dict(query.first(), template)
#     rule = ('object', 'objects')[int(iterable)]
#     return execute_rule(query, rule, template)
#
#
# execute_rule(object, 'objects', ())
#
#
# def pars_doc(query, template: tuple):
#     pass
#
#
# rules = {
#     'string': f_str,
#     'integer': f_int,
#     'float': f_float,
#     'boolean': f_bool,
#     'object': obj_to_dict,
#     'objects': objs_to_dict,
# }


