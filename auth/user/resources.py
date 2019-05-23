from datetime import datetime

import falcon

from falcon_core.resources import Resource, JSONResource

from gusto_api.models import User, Project, Group, Permission#, OpenTime
from gusto_api.utils import encrypt, filter_queryset, dict_from_model, model_from_dict
from auth.utils import delete_request, post_create_user, encrypt_password, validate_obj


class UsersResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET all users
        url: users/
        """

        users = filter_queryset(User.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(users, User.response_templates['short'], iterable=True)

    def on_post(self, req, resp, **kwargs):
        """
        POST(create) user
        url: users/
        """
        user = User(**req.context['data'])
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
        user = User.objects.filter(id=kwargs['id']).first()
        if user:
            resp.status = falcon.HTTP_OK
            resp.media = dict_from_model(user, User.response_templates['short'])
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
        user = User.objects.filter(id=kwargs.get('id')).first()

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
        delete_request(User, resp, **kwargs)


class LoginResource(Resource):
    use_token = False

    def on_post(self, req, resp, **kwargs):
        """
        POST(login) user with given (email or telephone) and password and return user token
        url: users/login/
        """
        # users = [user.generate_token() for user in User.objects.all()]

        resp.status = falcon.HTTP_200
        data = req.context['data']
        if data.get('login') and data.get('password'):
            user = User.objects.filter(**{
                ('tel', 'email')[int(bool('@' in data['login']))]: data.pop('login')
            }).first()
            if user and user.password == encrypt_password(user, data['password']):
                resp.media = dict_from_model(user, User.response_templates['login'])
            else:
                raise falcon.HTTPUnauthorized('login or password don\'t match')
        else:
            raise falcon.HTTPBadRequest


class RegistrationResource(Resource):
    use_token = False

    def on_post(self, req, resp, **kwargs):
        data = req.context['data']
        [data['user'].pop(key, None) for key in set(User.fields.keys() ^ data['user'].keys())]
        [data['project'].pop(key, None) for key in set(Project.fields.keys() ^ data['project'].keys())]
        user = User(**data['user'])

        user.password = encrypt(user.email + user.tel + user.password)
        user.date_created = datetime.now()
        user.last_login = datetime.now()
        user.is_active = True

        project = Project(**data['project'])

        for instance in [user, project]:
            error = validate_obj(instance)
            if error:
                resp.status = falcon.HTTP_400
                print(error, 1)
                resp.body = error
                return
        user.save()
        project.save()
        work_times = []
        # for w_time in data['working_time']:
        #     # w_t = OpenTime(**w_time)
        #     w_t.project = project.id
        #     w_t.save()
        #     work_times.append(w_t)
        group = Group(users=[str(user.id)], project=str(project.id), name=project.name,
                       permissions=[str(perm.id) for perm in Permission.objects.all()], g_type='restaurant')
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
        resp.media = {'user': dict_from_model(user, User.response_templates['login']),
                      'group': dict_from_model(group, Group.response_templates['short']),
                      'project': dict_from_model(project, Project.response_templates['short'])
                      }
        resp.status = falcon.HTTP_200
