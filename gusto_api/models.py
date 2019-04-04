from mongoengine import *

connect('tests')


class LanguageTemplate(EmbeddedDocument):
    en = StringField(max_length=255)
    ru = StringField(max_length=255)
    uk = StringField(max_length=255)

    def __str__(self):
        return f"<LanguageTemplate en={self.en}, ru={self.ru}, uk={self.uk}>"


class FileTemplate(EmbeddedDocument):
    meta = {
        "allow_inheritance": True
    }

    url = StringField()


class ImageTemplate(FileTemplate):
    thumbnail = StringField()
    small = StringField()
    medium = StringField()
    large = StringField()

    def __str__(self):
        return f"<ImageTemplate thumbnail={self.thumbnail}, small={self.small}, large={self.large}>"


class Projects(Document):
    name = EmbeddedDocumentField(LanguageTemplate)
    domain = StringField(unique=True)
    additional_domains = LineStringField()
    address = EmbeddedDocumentListField(LanguageTemplate)
    logo = EmbeddedDocumentField(ImageTemplate)
    favicon = EmbeddedDocumentField(ImageTemplate)

    @property
    def groups(self):
        return Groups.objects.filter(project=self)

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
              'login': str,
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
    date_created = DateField()
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

    def group_values(self, col_name):
        return Groups.objects(col_name)

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


class UsersTokens(Document):
    fields = {'user': int,
              'token': str}

    user = ReferenceField(Users)
    token = StringField()

    def __str__(self):
        return f"<Group id={self.id}, user={self.user}, token={self.token}>"