from mongoengine import *
from datetime import datetime
from .models_description import (currencies, cities, sms, users_tokens, groups,
                                 countries, users, groups_templates, projects, posts, openTime, permissions)
from falcon_core.utils import encrypt_sha256_with_secret_key

connect('gusto')


class LanguageTemplate(EmbeddedDocument):
    fields_list = ['en', 'ru', 'uk']
    en = StringField(max_length=255)
    ru = StringField(max_length=255)
    uk = StringField(max_length=255)

    def get_created(self):
        response = {}
        for i in self.fields_list:
            if getattr(self, i) is not None:
                response[i] = getattr(self, i)
        return response

    def __str__(self):
        return f"<LanguageTemplate en={self.en}, ru={self.ru}, uk={self.uk}>"


class FileTemplate(EmbeddedDocument):
    meta = {
        "allow_inheritance": True
    }

    url = StringField()


class ImageTemplate(FileTemplate):
    fields = {}

    thumbnail = StringField()
    small = StringField()
    medium = StringField()
    large = StringField()

    def __str__(self):
        return f"<ImageTemplate thumbnail={self.thumbnail}, small={self.small}, large={self.large}>"


class Permission(Document):
    ACCESSES = ('read', 'write')

    fields = {'name': str,
              'access': int,
              'description': str
              }

    unique_fields = []

    response_template = permissions['response_template']

    name = StringField()
    access = IntField()
    description = StringField()

    @property
    def get_access(self):
        return f"{self.name}_{self.ACCESSES[self.access]}"

    def __str__(self):
        return f"<Permission id={self.id}, name={self.name}, access={self.access}>"


class User(Document):
    fields = users['fields']

    unique_fields = []
    name = StringField()
    surname = StringField()
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    last_login = DateTimeField()
    is_active = BooleanField(default=True)
    date_created = DateTimeField()
    image = StringField()
    tel = StringField(max_length=24, unique=True, required=True)

    @property
    def get_last_login(self):
        if self.last_login is None:
            return None
        return datetime.timestamp(self.last_login)

    @property
    def get_date_created(self):
        if self.date_created is None:
            return None
        return datetime.timestamp(self.date_created)

    def generate_token(self):
        groups = Group.objects.filter(users__contains=str(self.id))
        permissions = []
        # print(groups.values_list('permissions'))
        for perms in groups.values_list('permissions'):
            permissions.extend(perms)

        # print(permissions)
        permissions = '__'.join([f'{perm.id}_{perm.get_access}' for perm in permissions])
        # print(permissions)

        token = encrypt_sha256_with_secret_key(str(self.id) + self.email + self.tel + self.password + permissions)
        user_token = UserToken.objects.filter(user=self).first()
        if user_token:
            user_token.token = token
            user_token.save()
        else:
            UserToken(user=self, token=token).save()

    def __str__(self):
        return f"<User id={self.id}, tel={self.tel}, name={self.email}, password={self.password}>"


class SuperUser(Document):
    root = ReferenceField(User)


class Staff(Document):
    owner = ReferenceField(User)
    staff_list = ListField(ReferenceField(User, reverse_delete_rule=PULL))


class Project(Document):
    fields = projects['fields']

    unique_fields = projects['unique_fields']

    response_templates = projects['response_templates']

    name = StringField(required=True)
    domain = StringField(unique=True, required=True)
    additional_domains = ListField(StringField())
    address = EmbeddedDocumentListField(LanguageTemplate)
    is_active = BooleanField(default=True)
    logo = EmbeddedDocumentField(ImageTemplate)
    favicon = EmbeddedDocumentField(ImageTemplate)
    owner = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    p_type = StringField()

    @property
    def groups(self):
        return Group.objects.filter(project=self)

    def __str__(self):
        return f"<Project id={self.id}, domain={self.domain}, tel={self.address}, additional_domains={self.additional_domains}>"


class Group(Document):
    fields = groups['fields']

    temp_fields = groups['temp_fields']

    filters = groups['filters']

    response_templates = groups['response_templates']

    unique_fields = []

    users = ListField(ReferenceField(User, reverse_delete_rule=PULL))
    project = ReferenceField(Project, reverse_delete_rule=CASCADE, required=True)
    name = StringField(required=True)
    permissions = ListField(ReferenceField(Permission, reverse_delete_rule=PULL))
    g_type = StringField()  # add required soon...
    descriptions = StringField()

    def __str__(self):
        return f"<Group id={self.id}, name={self.name},  users={self.users}, project={self.project.name}>"


class GroupTemplate(Document):
    fields = groups_templates['fields']

    name = StringField()
    permissions = ListField(ReferenceField(Permission, reverse_delete_rule=PULL))
    g_type = StringField()

    def __str__(self):
        return f"<GroupTemplates id={self.id}, name={self.name}, permissions={self.permissions}>"


class UserToken(Document):
    fields = users_tokens['fields']

    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    token = StringField()

    def __str__(self):
        return f"<Group id={self.id}, user={self.user}, token={self.token}>"


class SMS(Document):
    fields = sms['fields']

    tel = StringField()
    code = StringField()
    created = DecimalField()
    expire = DecimalField()


#
#
# class Currencies(Document):
#     fields = currencies['fields']
#
#     unique_fields = currencies['unique_fields']
#
#     response_template = currencies['response_template']
#
#     name = StringField(required=True)
#     symbol = StringField(required=True)
#     code = StringField(unique=True, required=True)
#     rate = IntField()
#     rates = ListField()
#     last_update = DateTimeField()
#
#     @property
#     def get_last_update(self):
#         return datetime.timestamp(self.last_update)
#
#     def __str__(self):
#         return f"<Currencies id={self.id}, name={self.name}, symbol={self.symbol}, code={self.code}>"
#

# class Countries(Document):
#     fields = countries['fields']
#
#     response_template = countries['response_template']
#
#     unique_fields = countries['unique_fields']
#
#     name = StringField(required=True)
#     iso2 = StringField(unique=True, required=True)
#     dial_code = StringField()
#     priority = IntField(required=True)
#     area_codes = ListField()
#     currency = ReferenceField(Currencies, reverse_delete_rule=NULLIFY)
#
#     def __str__(self):
#         return f"<Currencies id={self.id}, name={self.name}, iso2={self.iso2}, currency={self.currency}>"

#
# class Cities(Document):
#     fields = cities['fields']
#
#     response_templates = cities['response_templates']
#
#     unique_fields = []
#
#     active = BooleanField(default=True)
#     country_code = StringField(required=True)
#     default = BooleanField(default=False)
#     name = StringField(required=True)
#     lat = IntField()
#     lng = IntField()
#     language = EmbeddedDocumentField(LanguageTemplate, required=True)
#     number_phone = StringField()
#     exist_store = BooleanField(default=False)
#
#     def __str__(self):
#         return f"<City id={self.id} country_code={self.country_code}, name={self.name}>"

#
# class PostCategories(Document):
#     fields = {'name': str}
#
#     unique_fields = []
#
#     response_templates = (('name', 'string',),)
#
#     name = StringField()


# class Posts(Document):
#     fields = posts['fields']
#
#     unique_fields = []
#
#     response_templates = posts['response_templates']
#
#     title = EmbeddedDocumentField(LanguageTemplate)
#     author = StringField()
#     post_category = ReferenceField(PostCategories, reverse_delete_rule=CASCADE)
#     project = ReferenceField(Project, reverse_delete_rule=CASCADE)
#     tags = ListField(StringField())
#     url = StringField()
#     content = EmbeddedDocumentField(LanguageTemplate)
#     date_created = DateTimeField()
#     last_update = DateTimeField()


class OpenTime(Document):
    fields = openTime['fields']

    unique_fields = []

    response_templates = openTime['response_templates']

    day = IntField()
    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    open_hours = IntField()
    open_minutes = IntField()
    close_minutes = IntField()
    close_hours = IntField()
