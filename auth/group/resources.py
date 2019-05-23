import falcon
from falcon_core.resources import Resource
from gusto_api.utils import filter_queryset, dict_from_model
from gusto_api.models import Group, Project, User, Permission


class GroupsResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        groups = filter_queryset(Group.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(groups, Group.response_templates['long'], iterable=True)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) group
        url: groups/
        """
        data = req.context['data']
        if data != {}:
            group = Group(**data)
            group.save()
            resp.media = dict_from_model(group, Group.response_templates['long'])
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class GroupResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET group by id
        url: groups/{id}/
        """
        if kwargs.get('id'):
            group = Group.objects.filter(id=kwargs['id']).first()
        else:
            group = Group.objects.filter(project=kwargs['project_id']).first()
        if group is None:
            resp.status = falcon.HTTP_404
            return
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(group, Group.response_templates['long'])

    def on_put(self, req, resp, **kwargs):
        """
        PUT group by id with given data
        url: groups/{id}/
        """

        data = req.context['data']

        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_400
            return

        if data != {}:

            group = Group.objects.filter(**kwargs).first()

            if group is None:
                resp.status = falcon.HTTP_404
                return

            if data.get('project', False):
                project = Project.objects.filter(id=data['project']).first()
                if project:
                    data['project'] = project

            if data.get('users', False):
                users = []
                for user in data['users']:
                    user = User.objects.filter(id=user).first()
                    if user is not None:
                        users.append(user)
                data['users'] = users

            if data.get('permissions', False):
                permissions = []
                for perm in data['permissions']:
                    perm = Permission.objects.filter(id=perm).first()
                    if perm is not None:
                        permissions.append(perm)
                data['permissions'] = permissions

            group.update(**data)
            resp.media = dict_from_model(group, Group.response_templates['long'])
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST

    def on_delete(self, req, resp, **kwargs):
        """
        DELETE group by id
        url: groups/{id}/
        """
        if kwargs.get('id'):
            Group.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
