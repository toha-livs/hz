

def list_obj_to_serialize_format(list_obj: list, recurs=None):
    response_list = []
    for obj in list_obj:
        print(obj)
        var_dict = obj.to_dict(table_name=True)
        print(var_dict)
        if recurs:
            if var_dict.get('table_name') == 'users':
                var_dict['groups'] = list_obj_to_serialize_format(obj.groups())
            ##
            ## if groups
            ##
        response_list.append(var_dict)
    return response_list