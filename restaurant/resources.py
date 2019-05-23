import datetime

import falcon
from falcon_core.resources import Resource

from gusto_api.models import Project, OpenTime, Permission, Group, User, UserToken
from gusto_api.utils import dict_from_model


class WorkingTimeResource(Resource):
    use_token = True  # edit

    def on_get(self, req, resp, **kwargs):
        # filter(lambda group: bool(f'{OpenTime.__module__}.{OpenTime.__name__}' in group.permissions), req.context['user']['groups'])
        perm = Permission.objects.filter(name='working_time', access=0).first()
        if Group.objects.filter(project=req.params['project_id'], permissions__contains=str(perm.id), users__contains=str(self.storage['token'].user.id)):
            print('True')
            resp.media = dict_from_model(OpenTime.objects.filter(project=req.params['project_id']).first(), OpenTime.response_templates['short'])
        else:
            print('false')
            resp.media = {'you': 'none'}
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, **kwargs):
        """
        POST(create) user
        url: users/
        """
        # project = Project.objects.filter(id=req.params.get('project_id')).first()
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
