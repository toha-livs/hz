import json
import falcon

from falcon_core.resources import Resource, JSONResource
from mongoengine import Q

from gusto_api.models import Users, Projects, Groups, Permissions
from gusto_api.utils import encrypt, filter_queryset, dict_from_model, model_from_dict
from auth.utils import delete_request, post_create_user, encrypt_password


class UsersResource(JSONResource):

    use_token = True

    def on_get(self, req, resp, **kwargs):
        """
        GET all users
        url: users/
        """

        users = filter_queryset(Users.objects, **req.params)
        resp.status = falcon.HTTP_OK
        resp.media = dict_from_model(users, Users.temp_fields['default'], iterable=True)

    def post(self, req, resp, data, **kwargs):
        """
        POST(create) user
        url: users/
        """
        user = Users(**data)
        print('before valid')
        user, error = user.check_valid_unique()
        if user:
            user.save()
            resp.status = falcon.HTTP_201
        else:
            resp.status = falcon.HTTP_400
            resp.body = error
            return
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
            resp.media = dict_from_model(user, Users.temp_fields['default'])
        else:
            resp.status = falcon.HTTP_404

    def post(self, req, resp, data, **kwargs):
        """
        POST(create) user via registration
        url: users/registration/
        """
        post_create_user(req, resp, data)

    def put(self, req, resp, data, **kwargs):
        """
        PUT user by id with given data
        url: users/{id}/
        """
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

    def post(self, req, resp, data, **kwargs):
        """
        POST(login) user with given (email or telephone) and password and return user token
        url: users/login/
        """

        if data.get('login') and data.get('password'):
            user = Users.objects.filter(**{
                ('tel', 'email')[int(bool('@' in data['login']))]: data.pop('login')
            }).first()
            if user and user.password == encrypt_password(user, data['password']):
                resp.media = dict_from_model(user, Users.temp_fields['default'])
            else:
                raise falcon.HTTPUnauthorized
        else:
            raise falcon.HTTPBadRequest


class RegistrationResource(JSONResource):

    use_token = True

    def post(self, request, response, data, **kwargs):
        # print(data)
        # data['user'].pop('tel')
        user = Users(**data['user'])
        project = Projects(**data['project'])
        try:
            user.validate()
            project.validate()
        except:
            print('false')
            return
        print(user)
        # user.save()
        # project.save()
        # print('###user')
        print(user, dir(user))
        # print('###user')
        # test_user = model_from_dict(data['user'], (Users, (
        #     ('name:require', 'string'),
        #     ('surname', 'string'),
        #     ('tel:require', 'string'),
        #     ('email:require', 'string'),
        #     ('image', 'string'),
        # )))
        # print(test_user)
        # if Users.objects.filter((Q(email=test_user.email) or (Q(tel=test_user.tel)))):
        #     print('user is already exist')
        #     test_user = None
        # test_project = model_from_dict(data['project'], (Projects, (
        #     ('name:require', 'string'),
        #     ('domain:require', 'string'),
        # )))
        # print(test_project)
        # test_group = Groups()
        # user = post_create_user(request, response, data['user'])
        # print(user, dir(user), user.id)
        # print('user save')
        # same_fields = set(data['project'].keys() ^ set(Projects.fields.keys()))
        # print(f'same fields {same_fields}')
        # [data['project'].pop(key, None) for key in same_fields]
        # project = Projects(**data['project'])
        # project.save()
        # print('project save')
        # if test_user is not None and test_project is not None:
        #     print('save()')
        #     test_user.save()
        #     test_project.save()
        #     group = Groups(users=[str(test_user.id)], project=str(test_project.id), name=test_project.name + '_Group',
        #                    permissions=[str(perm.id) for perm in Permissions.objects.all()], g_type='restaurant')
        #     group.save()
        # else:
        #     print('lazha')
        # print('group save')
        # response.media = dict_from_model(user, Users.temp_fields)
        # #     (
        # #     ('id', 'string'),
        # #     ('name', 'string'),
        # #     ('email', 'string'),
        # #     ('tel', 'string'),
        # #     ('get_last_login:last_login', 'float'),
        # #     ('get_date_created:date_created', 'float'),
        # #     ('token', 'string'),
        # #     ('groups', 'objects', (
        # #         ('name', 'string'),
        # #         ('permissions', 'objects', (
        # #             ('id', 'string'),
        # #             ('get_access:access', 'string'),
        # #         )),
        # #     )),
        # # ))
        # response.status = falcon.HTTP_201
        response.status = falcon.HTTP_200
