import datetime

import falcon
from falcon_core.resources import Resource

from gusto_api.models import Projects, OpenTime
from gusto_api.utils import dict_from_model


class WorkingTimeResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        # project = Projects.objects.filter(id=req.params.get('project_id')).first()
        # if not project:
        #     resp.status = falcon.HTTP_404
        #     return
        # working_time = OpenTime.objects.filter(project=str(project.id))
        # print(working_time)
        resp.media = dict_from_model(OpenTime.objects.all(), OpenTime.response_templates['short'], iterable=True)
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, **kwargs):
        """
        POST(create) user
        url: users/
        """
        # project = Projects.objects.filter(id=req.params.get('project_id')).first()
        # if not project:
        #     resp.status = falcon.HTTP_404
        #     return
        data = req.context['data']
        for day in data:
            work_day = OpenTime.objects.filter(day=day['day']).first()
            if not work_day:
                resp.status = falcon.HTTP_400
                return
            work_day.update(**day)
        resp.status = falcon.HTTP_201
