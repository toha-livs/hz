import falcon
from falcon_core.resources import Resource
from gusto_api.utils import filter_queryset, dict_from_model
from gusto_api.models import Groups, Projects, Users, Permissions


class GroupsResource(Resource):
    use_token = True

    def get(self, req, resp, **kwargs):
        groups = filter_queryset(Groups.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(groups, (
            ('id', 'string'),
            ('name', 'string'),
            ('g_type', 'string'),
            ('is_owner', 'boolean'),
            ('project', 'object', (
                ('id', 'string'),
                ('name', 'object', (
                    ('en', 'string'),
                    ('ru', 'string'),
                    ('uk', 'string'),
                )),
                ('additional_domains', 'list'),

            )),
            ('permissions', 'objects', (
                ('name', 'string'),
                ('access', 'integer')
            )),
        ), iterable=True)

    def post(self, req, resp, data, **kwargs):
        """
        POST(create) group
        url: groups/
        """
        if data != {}:
            group = Groups(**data)
            group.save()
            resp.media = dict_from_model(group, (
                ('id', 'string'),
                ('name', 'string'),
                ('g_type', 'string'),
                ('is_owner', 'boolean'),
                ('users', 'objects', (
                    ('name', 'string'),
                    ('email', 'string'),
                    ('is_active', 'boolean'),
                    ('image', 'string'),
                )),
                ('project', 'object', (
                    ('id', 'string'),
                    ('name', 'object', (
                        ('en', 'string'),
                        ('ru', 'string'),
                        ('uk', 'string'),
                    )),

                )),
                ('permissions', 'objects', (
                    ('name', 'string'),
                    ('access', 'integer')
                )),
            ))
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST


class GroupResource(Resource):
    use_token = True

    def get(self, req, resp, **kwargs):
        """
        GET group by id
        url: groups/{id}/
        """
        if kwargs.get('id'):
            group = Groups.objects.filter(id=kwargs['id']).first()
        else:
            group = Groups.objects.filter(project=kwargs['project_id']).first()
        if group is None:
            resp.status = falcon.HTTP_404
            return
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(group, (

            ('id', 'string'),
            ('name', 'string'),
            ('g_type', 'string'),
            ('is_owner', 'boolean'),
            ('users', 'objects', (
                ('name', 'string'),
                ('email', 'string'),
                ('is_active', 'boolean'),
                ('image', 'string'),
            )),
            ('project', 'object', (
                ('id', 'string'),
                ('name', 'object', (
                    ('en', 'string'),
                    ('ru', 'string'),
                    ('uk', 'string'),
                )),
            )),
            ('permissions', 'objects', (
                ('name', 'string'),
                ('access', 'integer')
            )),
        ))

    def put(self, req, resp, data, **kwargs):
        """
        PUT group by id with given data
        url: groups/{id}/
        """

        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_400
            return

        if data != {}:

            group = Groups.objects.filter(**kwargs).first()

            if group is None:
                resp.status = falcon.HTTP_404
                return

            if data.get('project', False):
                project = Projects.objects.filter(id=data['project']).first()
                if project:
                    data['project'] = project

            if data.get('users', False):
                users = []
                for user in data['users']:
                    user = Users.objects.filter(id=user).first()
                    if user is not None:
                        users.append(user)
                data['users'] = users

            if data.get('permissions', False):
                permissions = []
                for perm in data['permissions']:
                    perm = Permissions.objects.filter(id=perm).first()
                    if perm is not None:
                        permissions.append(perm)
                data['permissions'] = permissions

            group.update(**data)
            resp.media = dict_from_model(group, (
                ('id', 'string'),
                ('name', 'string'),
                ('g_type', 'string'),
                ('is_owner', 'boolean'),
                ('users', 'objects', (
                    ('name', 'string'),
                    ('email', 'string'),
                    ('is_active', 'boolean'),
                    ('image', 'string'),
                )),
                ('project', 'object', (
                    ('id', 'string'),
                    ('name', 'object', (
                        ('en', 'string'),
                        ('ru', 'string'),
                        ('uk', 'string'),
                    )),
                )),
                ('permissions', 'objects', (
                    ('name', 'string'),
                    ('access', 'integer')
                )),
            ))
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST

    def delete(self, req, resp, data, **kwargs):
        """
        DELETE group by id
        url: groups/{id}/
        """
        if kwargs.get('id'):
            Groups.objects.filter(id=kwargs['id']).first().delete()
        else:
            raise falcon.HTTPNotFound
