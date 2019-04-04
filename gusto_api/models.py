from mongoengine import *

connect('tests')


class Groups(Document):

    users_ids = ListField()
    project_id = StringField(null=False)
    name = StringField(nullable=False)
    permissions_ids = ListField()
    g_type = StringField()
    is_owner = BooleanField()

    filters = {
        'users': 'filter_users'
    }

    fields = {'users_ids': list,
              'name': str,
              'permissions_ids': list,
              'g_type': str,
              'is_owner': bool, }
    temp_fields = ['users']
    #
    # @property
    # def project(self):
    #     return json.loads(Project.objects.filter(id=self.project_id).first().to_json())
    #
    # def __repr__(self):
    #     return '<Groups id={}, users_ids={}, permission_ids={}>'.format(self.pk, self.users_ids, self.permissions_ids)
    #
    # @property
    # def users(self):
    #     users = session.query(Users).filter(Users.pk.in_(self.users_ids)).all()
    #     session.close()
    #     return users
    #
    # def filter_users(self, **kwargs):
    #     users = session.query(Users).filter_by(**kwargs).all()
    #     session.close()
    #     return users
    #
    # @property
    # def permissions(self):
    #     permissions = session.query(Permissions).filter(Permissions.pk.in_(self.permissions_ids)).all()
    #     session.close()
    #     return permissions

