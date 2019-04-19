from mongoengine import *

from falcon_core.utils import encrypt_sha256_with_secret_key

connect('gusto_api')


class Users(Document):
    name = StringField()
    surname = StringField()
    email = EmailField(unique=True, required=True)
    tel = StringField(unique=True, required=True)
    last_login = DateTimeField()
    date_created = DateTimeField()
    password = StringField()

    to_dict = (
        ('name', 'string'),
        ('surname', 'string'),
        ('email', 'string'),
        ('tel', 'string'),
        ('last_login', 'string'),
        ('date_created', 'string'),
        ('groups', 'objects', (
            ('name', 'string'),
            ('permissions', 'objects', (
                ('name', 'string'),
            )),
        )),
    )

    @property
    def groups(self):
        return Groups.objects.filter(users__in=[self.id])

    def generate_token(self):
        groups = Groups.objects.filter(users__in=[self.id])
        permissions = []
        for perms in groups.values_list('permissions'):
            permissions.extend(perms)
        permissions = '__'.join([f'{perm.id}_{perm.get_access()}' for perm in permissions])
        token = encrypt_sha256_with_secret_key(self.id + self.email + self.tel + self.password + permissions)
        user_token = UsersTokens.objects.filter(user=self).first()
        if user_token:
            user_token.token = token
            user_token.save()
        else:
            UsersTokens(user=self, token=token).save()

    def get_token(self):
        user_token = UsersTokens.objects.filter(user=self).first()
        if user_token:
            return user_token.token
        return None

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id}>'


class UsersTokens(Document):
    user = ReferenceField(Users)
    token = StringField()

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id}>'


class Permissions(Document):
    ACCESSES = {
        0: 'r',
        1: 'w',
    }

    name = StringField()
    access = IntField(choices=ACCESSES.keys())

    to_dict = (
        ('name', 'string'),
        ('get_access:access', 'string'),
    )

    @property
    def get_access(self):
        return f'{self.name}_{self.ACCESSES[self.access]}'

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id}>'


class Groups(Document):
    name = StringField()
    users = ListField(ReferenceField(Users))
    permissions = ListField(ReferenceField(Permissions))

    to_dict = (
        ('name', 'string'),
        ('users', 'objects'),
        ('permissions', 'string'),
    )

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id}>'
