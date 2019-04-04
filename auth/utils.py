import falcon
from .models import Groups
import json


def get_univ_filter(model_obj, params):
    sort = params.get('sort', 'id')
    if sort not in model_obj.fields:
        sort = 'id'
    elif sort == 'g_type':
        sort = 'type'
    off_set = int(params.get('offset', 0))
    limit = int(params.get('limit', 0))
    reqursions_step = int(params.get('recur', 1))
    print('good')