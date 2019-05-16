from datetime import datetime

import falcon

from falcon_core.resources import Resource, JSONResource

from gusto_api.models import Users, Projects, Groups, Permissions
from gusto_api.utils import encrypt, filter_queryset, dict_from_model, model_from_dict
from auth.utils import delete_request, post_create_user, encrypt_password, validate_obj


class UsersResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET all users
        url: users/
        """

        users = filter_queryset(Users.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(users, Users.response_templates['short'], iterable=True)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) user
        url: users/
        """
        user = Users(**req.context['data'])
        print('before valid')
        error = validate_obj(user)
        if error:
            resp.status = falcon.HTTP_400
            resp.body = error
            return
        user.save()
        resp.status = falcon.HTTP_201
        # post_create_user(req, resp, data)


class UserResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET user by id
        url: users/{id}/
        """
        user = Users.objects.filter(id=kwargs['id']).first()
        if user:
            resp.status = falcon.HTTP_OK
            resp.media = dict_from_model(user, Users.response_templates['short'])
        else:
            resp.status = falcon.HTTP_404

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) user via registration
        url: users/registration/
        """
        post_create_user(req, resp, req.context['data'])

    def on_put(self, req, resp, **kwargs):
        """
        PUT user by id with given data
        url: users/{id}/
        """
        data = req.context['data']
        user = Users.objects.filter(id=kwargs.get('id')).first()

        if user is None:
            resp.status = falcon.HTTP_404
            return
        if not data.get('password'):
            data.pop('password', None)
        else:
            data['password'] = encrypt(user.email + user.tel + data['password'])

        if not data.get('last_login'):
            data.pop('last_login', None)

        same_fields = {x: data[x] for x in user.fields & data.keys()}
        if same_fields:
            user.update(**same_fields)
            user.generate_token()
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, **kwargs):
        """
        DELETE user bu id
        url: users/{id}/
        """
        delete_request(Users, resp, **kwargs)


class LoginResource(Resource):
    use_token = False

    def on_post(self, req, resp, **kwargs):
        """
        POST(login) user with given (email or telephone) and password and return user token
        url: users/login/
        """
        data = req.context['data']
        if data.get('login') and data.get('password'):
            user = Users.objects.filter(**{
                ('tel', 'email')[int(bool('@' in data['login']))]: data.pop('login')
            }).first()
            if user and user.password == encrypt_password(user, data['password']):
                resp.media = dict_from_model(user, Users.response_templates['login'])
            else:
                raise falcon.HTTPUnauthorized('login or password don\'t match')
        else:
            raise falcon.HTTPBadRequest


class RegistrationResource(Resource):
    use_token = False

    def on_post(self, req, resp, **kwargs):
        # print(data)
        data = req.context['data']
        [data['user'].pop(key, None) for key in set(Users.fields.keys() ^ data['user'].keys())]
        [data['project'].pop(key, None) for key in set(Projects.fields.keys() ^ data['project'].keys())]
        user = Users(**data['user'])

        user.password = encrypt(user.email + user.tel + user.password)
        user.date_created = datetime.now()
        user.last_login = datetime.now()
        user.is_active = True

        project = Projects(**data['project'])

        for instance in [user, project]:
            error = validate_obj(instance)
            if error:
                resp.status = falcon.HTTP_400
                print(error, 1)
                resp.body = error
                return
        user.save()
        project.save()
        group = Groups(users=[str(user.id)], project=str(project.id), name=project.name,
                       permissions=[str(perm.id) for perm in Permissions.objects.all()], g_type='restaurant')
        error = validate_obj(group)
        if error:
            user.delete()
            project.delete()
            print(error, 3)
            resp.status = falcon.HTTP_400
            resp.body = error
            return
        group.save()
        user.generate_token()
        resp.media = {'user': dict_from_model(user, Users.response_templates['login']),
                      'group': dict_from_model(group, Groups.response_templates['short']),
                      'project': dict_from_model(project, Projects.response_templates['short'])
                      }
        resp.status = falcon.HTTP_200
