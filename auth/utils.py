from gusto_api.models import UsersTokens

# def token_exists(instance) -> bool:
#     """
#     Checks if given token exists in the database
#     :param instance: UsersToken object
#     :return: True or False
#     """
#     instance.token = UsersTokens.objects.filter(token=instance.token).first()
#     return bool(instance.token)

def get_univ_filter(model_obj, params):
    sort = params.get('sort', 'id')
    if sort not in model_obj.fields:
        sort = 'id'
    elif sort == 'g_type':
        sort = 'type'
    off_set = int(params.get('offset', 0))
    limit = int(params.get('limit', 0))
    # reqursions_step = int(params.get('recur', 1))
    print('good')