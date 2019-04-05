import json

import falcon
from falcon_core.resources import Resource

from gusto_api.models import Groups


class GroupsResource(Resource):

    def on_get(self, req, resp, **kwargs):
        fields = req.params
        sort = fields.pop('sort', 'id')
        # if sort not in Groups.fields:
        #     sort = 'id'
        # elif sort == 'g_type':
        #     sort = 'type'
        off_set = int(fields.pop('offset', 0))
        limit = int(fields.pop('limit', 0))
        reqursions_step = int(fields.pop('recur', 1))
        query_list = Groups.objects.filter(**req.params).order_by(sort)

        if limit:
            query_list = query_list[off_set:off_set + limit]
        try:
            for i in query_list:
                print(i.name)
            resp.media = json.loads(query_list.to_json())
            resp.status = falcon.HTTP_200

        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_404
