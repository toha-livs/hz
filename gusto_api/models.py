from mongoengine import *
from datetime import datetime, time, date

connect('tests1')


class Currencies(Document):
    name = StringField()
    symbol = StringField()
    code = StringField(unique=True)
    rate = IntField()
    rates = IntField()
    last_update = DateField()

    def to_dict(self):
        return dict(id=str(self.id), name=self.name, symbol=self.symbol, code=self.code, rate=self.rate,
                    rates=self.rates, lastUpdate=datetime.timestamp(datetime.combine(self.last_update, time.min)))

    def __str__(self):
        return f"<Currencies id={self.id}, name={self.name}, symbol={self.symbol}, code={self.code}>"


class Countries(Document):
    name = StringField()
    iso2 = StringField(unique=True)
    dial_code = StringField()
    priority = IntField()
    area_codes = ListField()
    currency = ReferenceField(Currencies)

    def __str__(self):
        return f"<Currencies id={self.id}, name={self.name}, iso2={self.iso2}, currency={self.currency}>"


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


class Cities(Document):
    fields = {
        'name': LanguageTemplate,
        'country_code': str,
        'default': bool,
        'active': str,
        'lat': int,
        'lng': int,
        'language': str,
        'number_phone': str,
        'exist_store': bool
    }

    active = BooleanField()
    country_code = StringField(required=True)
    default = BooleanField()
    name = EmbeddedDocumentField(LanguageTemplate)
    lat = IntField()
    lng = IntField()
    language = StringField()
    number_phone = StringField()
    exist_store = BooleanField()

    def to_dict(self, table_name=None):
        return {'name': self.name.get_created(),
                'country_code': self.country_code,
                'default': self.default,
                'active': self.active,
                'lat': self.lat,
                'lng': self.lng,
                'language': self.language,
                'number_phone': self.number_phone,
                'exist_store': self.exist_store
                }

    def __str__(self):
        return f"<City id={self.id} country_code={self.country_code}, name={self.name}>"


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
    fields = {
        'name': str,
        'domain': str,
        'additional_domains': list,
        'address': list,
        'logo': ImageTemplate,
        'favicon': ImageTemplate
    }
    name = EmbeddedDocumentField(LanguageTemplate)
    domain = StringField(unique=True)
    additional_domains = LineStringField()
    address = EmbeddedDocumentListField(LanguageTemplate)
    logo = EmbeddedDocumentField(ImageTemplate)
    favicon = EmbeddedDocumentField(ImageTemplate)

    @property
    def groups(self):
        return Groups.objects.filter(project=self)

    def to_dict(self, table_name=False):
        response = dict(id=str(self.id),
                        name={x: getattr(self.name, x) for x in self.name} if self.name is not None else {},
                        domain=self.domain,
                        additional_domains=self.additional_domains,
                        address={x: getattr(self.address, x) for x in self.address} if self.address is not None else {},
                        logo={x: getattr(self.logo, x) for x in self.logo} if self.logo is not None else {},
                        favicon={x: getattr(self.favicon, x) for x in self.favicon} if self.favicon is not None else {})

        if table_name:
            response.update({'table_name': 'projects'})
        return response

    def __str__(self):
        return f"<Projects id={self.id}, domain={self.domain}, tel={self.address}>"


class Permissions(Document):
    ACCESSES = ('r', 'w')

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
    fields = {
        'name': str,
        'permissions': list,
        'g_type': str
    }
    name = StringField()
    permissions = ListField(ReferenceField(Permissions))
    g_type = StringField()

    def __str__(self):
        return f"<GroupTemplates id={self.id}, name={self.name}, permissions={self.permissions}>"


class Users(Document):
    fields = {'name': str,
              'email': str,
              'password': str,
              'last_login': int,
              'is_active': bool,
              'image': str,
              'tel': str}

    temp_fields = [
        'groups'
    ]

    filters = {
        'groups': 'filter_groups'
    }

    name = StringField()
    email = EmailField()
    password = StringField()
    last_login = DateTimeField()
    date_created = DateTimeField()
    is_active = BooleanField()
    image = StringField()
    tel = StringField(max_length=24)

    @property
    def groups(self):
        return Groups.objects.filter(users__in=[self])

    @property
    def get_token(self):
        return UsersTokens.objects.filter(user=self).first()

    @staticmethod
    def filter_groups(**kwargs):
        return Groups.objects.filter(**kwargs).all()

    def to_dict(self, table_name=False):
        response = dict(id=str(self.id), name=self.name, email=self.email,
                        last_login=datetime.timestamp(self.last_login),
                        date_created=datetime.timestamp(datetime.combine(self.date_created, time.min)),
                        is_active=self.is_active, image=self.image, tel=self.tel)
        if table_name:
            response.update({'table_name': 'users'})
        return response

    def groups_values(self, col_name):
        return self.groups.values_list(col_name)

    def __str__(self):
        return f"<Users id={self.id}, email={self.email}, tel={self.tel}>"


class Groups(Document):
    fields = {
        'users': list,
        'name': str,
        'permissions': list,
        'g_type': str,
        'is_owner': bool
    }

    temp_fields = [
        'users'
    ]

    filters = {
        'users': 'filter_users'
    }

    users = ListField(ReferenceField(Users))
    project = ReferenceField(Projects)
    name = StringField()
    permissions = ListField(ReferenceField(Permissions))
    g_type = StringField()
    is_owner = BooleanField()

    @staticmethod
    def filter_users(**kwargs):
        return Users.objects.filter(**kwargs).all()

    def __str__(self):
        return f"<Group id={self.id}, users={self.users}, project={self.project}>"

    def to_dict(self, table_name=False):
        response = dict(id=str(self.id), name=self.name,
                        project=str(self.project.id) if self.project else None,
                        permissions=[perm.get_access for perm in self.permissions],
                        g_type=self.g_type, is_owner=self.is_owner)
        if table_name:
            response.update({'table_name': 'groups'})
        return response


class UsersTokens(Document):
    fields = {'user': int,
              'token': str}

    user = ReferenceField(Users)
    token = StringField()

    def __str__(self):
        return f"<Group id={self.id}, user={self.user}, token={self.token}>"
