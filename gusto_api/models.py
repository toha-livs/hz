from mongoengine import *
from datetime import datetime
from .models_description import (currencies, cities, sms, users_tokens, groups,
                                 countries, users, groups_templates, projects)
from falcon_core.utils import encrypt_sha256_with_secret_key

connect('tests')


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


class Projects(Document):
    fields = projects['fields']

    unique_fields = projects['unique_fields']

    response_templates = projects['response_templates']

    name = StringField(required=True)
    domain = StringField(unique=True, required=True)
    additional_domains = ListField(StringField())
    address = EmbeddedDocumentListField(LanguageTemplate)
    logo = EmbeddedDocumentField(ImageTemplate)
    favicon = EmbeddedDocumentField(ImageTemplate)

    @property
    def groups(self):
        return Groups.objects.filter(project=self)

    def __str__(self):
        return f"<Projects id={self.id}, domain={self.domain}, tel={self.address}, additional_domains={self.additional_domains}>"


class Permissions(Document):
    ACCESSES = ('r', 'w')

    unique_fields = []

    name = StringField()
    access = IntField()

    fields = {'name': str,
              'access': int}

    @property
    def get_access(self):
        return f"{self.name}_{self.ACCESSES[self.access]}"

    def __str__(self):
        return f"<Permissions id={self.id}, name={self.name}, access={self.access}>"


class GroupsTemplates(Document):
    fields = groups_templates['fields']

    name = StringField()
    permissions = ListField(ReferenceField(Permissions, reverse_delete_rule=PULL))
    g_type = StringField()

    def __str__(self):
        return f"<GroupTemplates id={self.id}, name={self.name}, permissions={self.permissions}>"


class Users(Document):
    fields = users['fields']

    temp_fields = users['temp_fields']

    response_templates = users['response_templates']

    filters = users['filters']

    unique_fields = users['unique_fields']

    name = StringField(required=True)
    surname = StringField()
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    last_login = DateTimeField()
    date_created = DateTimeField()
    is_active = BooleanField(default=True)
    image = StringField()
    tel = StringField(max_length=24, unique=True, required=True)

    #
    # def update(self, **kwargs):
    #     try:
    #         super(self).update(**kwargs)
    #         self.password =
    #     except:
    #         pass
    #
    @property
    def groups(self):
        return Groups.objects.filter(users__in=[self.id])

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
        groups = Groups.objects.filter(users__in=[self.id])
        permissions = []
        for perms in groups.values_list('permissions'):
            permissions.extend(perms)
        permissions = '__'.join([f'{perm.id}_{perm.get_access}' for perm in permissions])
        token = encrypt_sha256_with_secret_key(str(self.id) + self.email + self.tel + self.password + permissions)
        user_token = UsersTokens.objects.filter(user=self).first()
        if user_token:
            user_token.token = token
            user_token.save()
        else:
            UsersTokens(user=self, token=token).save()

    @property
    def token(self):
        user_token = UsersTokens.objects.filter(user=self).first()
        if user_token:
            return user_token.token
        return None

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id}>'


class Groups(Document):
    fields = groups['fields']

    temp_fields = groups['temp_fields']

    filters = groups['filters']

    response_templates = groups['response_templates']

    unique_fields = []

    users = ListField(ReferenceField(Users, reverse_delete_rule=PULL))
    project = ReferenceField(Projects, reverse_delete_rule=NULLIFY, required=True)
    name = StringField(required=True)
    permissions = ListField(ReferenceField(Permissions, reverse_delete_rule=PULL))
    g_type = StringField()  # add required soon...
    is_owner = BooleanField(default=False)

    def __str__(self):
        return f"<Group id={self.id}, name={self.name},  users={self.users}, project={self.project.name}>"


class UsersTokens(Document):
    fields = users_tokens['fields']

    user = ReferenceField(Users, reverse_delete_rule=CASCADE)
    token = StringField()

    def __str__(self):
        return f"<Group id={self.id}, user={self.user}, token={self.token}>"


class SMS(Document):
    fields = sms['fields']

    tel = StringField()
    code = StringField()
    created = DecimalField()
    expire = DecimalField()


class Currencies(Document):
    fields = currencies['fields']

    unique_fields = currencies['unique_fields']

    response_template = currencies['response_template']

    name = StringField(required=True)
    symbol = StringField(required=True)
    code = StringField(unique=True, required=True)
    rate = IntField()
    rates = ListField()
    last_update = DateTimeField()

    @property
    def get_last_update(self):
        return datetime.timestamp(self.last_update)

    def __str__(self):
        return f"<Currencies id={self.id}, name={self.name}, symbol={self.symbol}, code={self.code}>"


class Countries(Document):
    fields = countries['fields']

    response_template = countries['response_template']

    unique_fields = countries['unique_fields']

    name = StringField(required=True)
    iso2 = StringField(unique=True, required=True)
    dial_code = StringField()
    priority = IntField(required=True)
    area_codes = ListField()
    currency = ReferenceField(Currencies, reverse_delete_rule=NULLIFY)

    def __str__(self):
        return f"<Currencies id={self.id}, name={self.name}, iso2={self.iso2}, currency={self.currency}>"


class Cities(Document):
    fields = cities['fields']

    response_templates = cities['response_templates']

    unique_fields = []

    active = BooleanField(default=True)
    country_code = StringField(required=True)
    default = BooleanField(default=False)
    name = StringField(required=True)
    lat = IntField()
    lng = IntField()
    language = EmbeddedDocumentField(LanguageTemplate, required=True)
    number_phone = StringField()
    exist_store = BooleanField(default=False)

    def __str__(self):
        return f"<City id={self.id} country_code={self.country_code}, name={self.name}>"
