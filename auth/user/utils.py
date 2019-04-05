import json


def valid_json_obj(var_json):
    var_dict = json.loads(var_json)
    var_dict['id'] = var_dict['_id'].pop('$oid')
    var_dict.set('last_login', var_dict['last_login'])