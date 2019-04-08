import json

import falcon

from auth.resources import Resource
from auth.utils import get_request_multiple, delete_request, get_request_single
from gusto_api.models import Groups, Projects, Users, Permissions


class GroupsResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET all groups
        url: groups/
        """
        get_request_multiple(Groups, req.params, resp)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) group
        url: groups/
        """
        try:
            post_data = req.stream.read()

            if post_data:
                post_data = json.loads(post_data)
            else:
                post_data = {}

            group = Groups(**post_data)
            group.save()

            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400


class GroupResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET group by id
        url: groups/{id}/
        """
        get_request_single(Groups, resp, **kwargs)

    def on_put(self, req, resp, **kwargs):
        """
        PUT group by id with given data
        url: groups/{id}/
        """
        try:
            if 'id' not in kwargs.keys():
                resp.status = falcon.HTTP_400
                return

            group = Groups.objects.filter(**kwargs).first()

            if group is None:
                resp.status = falcon.HTTP_400
                return

            update_data = json.loads(req.stream.read())

            if update_data.get('project', False):
                project = Projects.objects.filter(id=update_data['project']).first()
                if project:
                    update_data['project'] = project

            if update_data.get('users', False):
                users = []
                for user in update_data['users']:
                    user = Users.objects.filter(id=user).first()
                    if user is not None:
                        users.append(user)
                update_data['users'] = users

            if update_data.get('permissions', False):
                permissions = []
                for perm in update_data['permissions']:
                    perm = Permissions.objects.filter(id=perm).first()
                    if perm is not None:
                        permissions.append(perm)
                update_data['permissions'] = permissions

            group.update(**update_data)

            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400

    def on_delete(self, req, resp, **kwargs):
        """
        DELETE group by id
        url: groups/{id}/
        """
        delete_request(Groups, resp, **kwargs)
