from falcon import HTTPBadRequest


def filter_queryset(queryset, req):
    offset, limit = req.params.pop('offset', None), req.params.pop('limit', None)

    try:
        queryset = queryset.filter(**req.params)
    except Exception as e:
        raise HTTPBadRequest(e)

    if limit and offset:
        queryset = queryset.skip(int(offset)).limit(int(limit))

    return queryset
