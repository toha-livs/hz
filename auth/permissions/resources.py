import falcon
from falcon_core.resources import Resource

from gusto_api.models import Group, Permission
from gusto_api.utils import dict_from_model


class PermissionsResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        group = Group.objects.filter(name='Administrators', project=req.params['projects_id'], users__contains=self.storage['token'].user.id)
        if not group:
            resp.status = falcon.HTTP_401
            return
        resp.media = dict_from_model(group.permissions, Permission.response_template['short'], iterable=True)
        resp.status = falcon.HTTP_200
