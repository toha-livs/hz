import os
import hashlib
from importlib import import_module

from falcon import HTTPBadRequest

from falcon_core.utils import dict_from_obj, obj_from_dict

os.environ.setdefault('FALCON_SETTINGS_MODULE', 'gusto_api.settings')


def import_object(module, default=None):
    module = module.split('.')
    return getattr(import_module('.'.join(module[:-1])), module[-1], default)


def encrypt(text: str) -> str:
    """
    Encrypt given text string using sha256
    :param text: string for encryption
    :return: encrypted string
    """
    secret_key = import_module(os.environ.get('FALCON_SETTINGS_MODULE')).SECRET_KEY
    return hashlib.sha256(str(text + secret_key).encode()).hexdigest()


def filter_queryset(queryset, **kwargs):
    offset, limit, order_by = kwargs.pop('offset', 0), kwargs.pop('limit', None), kwargs.pop('order_by', None)

    queryset = queryset.filter(**kwargs)

    queryset = queryset.skip(int(offset))

    if limit:
        queryset = queryset.limit(int(limit))

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


def dict_from_model(queryset, data, iterable=False):
    return dict_from_obj(queryset, data, iterable)


def model_from_dict(obj_dict, data, iterable=False):
    try:
        obj = obj_from_dict(obj_dict, data, iterable)
    except ValueError:

        return (None, 'val error',)
    except KeyError:
        return (None, 'key error')
    return obj
