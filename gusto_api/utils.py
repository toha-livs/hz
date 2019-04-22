from falcon import HTTPBadRequest

from falcon_core.utils import dict_from_obj


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
    try:
        return dict_from_obj(queryset, data, iterable)
    except Exception:
        raise HTTPBadRequest
