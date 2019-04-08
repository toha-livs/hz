from falcon_core.resources import Resource
import falcon
from gusto_api.models import Projects
import json


class ProjectResource(Resource):
    use_token = True

    def on_delete(self, req, resp, **kwargs):
        project = Projects.objects.filter(id=kwargs.get('id'))
        if not project:
            resp.status = falcon.HTTP_404
            return
        project.delete()
        resp.status = falcon.HTTP_204

    def on_put(self, req, resp, **kwargs):
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_404
                return
            project = Projects.objects.filter(**kwargs).first()
            if not project:
                resp.status = falcon.HTTP_400
                return
            update_data = json.loads(req.stream.read())
            project.update(**update_data)
            if project:
                project.save()
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_400

        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400
