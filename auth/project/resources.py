import json

import falcon
from falcon_core.resources import Resource

from gusto_api.models import Projects, Groups
from auth.utils import delete_request
from gusto_api.utils import dict_from_model


class ProjectResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        get project by group id
        url: projects/{group_id}/
        """
        print(kwargs)
        if kwargs.get('group_id'):
            group_id = kwargs.pop('group_id', None)
            kwargs['id'] = Groups.objects.filter(id=group_id).first().project.id
            print(kwargs['id'], 'groups')
        if not kwargs.get('id', False):
            resp.status = falcon.HTTP_404
            return
        resp.status = falcon.HTTP_OK
        print(kwargs.get('id'))
        project = Projects.objects.filter(id=kwargs.get('id')).first()
        print(project)
        resp.media = dict_from_model(project, Projects.response_templates['short'])

    def on_post(self, req, resp, **kwargs):
        """
        Post(create) project
        url: projects/
        """
        data = req.context['data']
        if not data:
            resp.status = falcon.HTTP_400
            return

        try:
            new_project = Projects(**data)
            new_project.save()
        except Exception as e:
            print(e)
            resp.body = 'Error on commit.'
            resp.status = falcon.HTTP_400
            return
        resp.media = dict_from_model(new_project, Projects.response_templates['short'])
        resp.status = falcon.HTTP_201

    def on_put(self, req, resp, **kwargs):
        """
        PUT project by id with given data
        url: projects/{id}/
        """
        data = req.context['data']
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_400
                return

            project = Projects.objects.filter(**kwargs).first()

            if project is None:
                resp.status = falcon.HTTP_400
                return

            if data != {}:
                project.update(**data)
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_BAD_REQUEST
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400

    def on_delete(self, req, resp, **kwargs):
        """
        DELETE project by id
        url: projects/{id}/
        """
        delete_request(Projects, resp, **kwargs)
