from mongoengine import *

connect('tests')


class LanguageTemplate(EmbeddedDocument):
    en = StringField(max_length=255)
    ru = StringField(max_length=255)
    uk = StringField(max_length=255)


class FileTemplate(EmbeddedDocument):
    meta = {
        "allow_inheritance": True
    }

    url = StringField(null=False)


class ImageTemplate(FileTemplate):
    thumbnail = StringField(null=False)
    small = StringField(null=False)
    medium = StringField(null=False)
    large = StringField(null=False)


class Project(Document):
    name = EmbeddedDocumentField(LanguageTemplate, null=False)
    domain = StringField(unique=True, null=False)
    additional_domains = LineStringField()
    address = EmbeddedDocumentListField(LanguageTemplate)
    logo = EmbeddedDocumentField(ImageTemplate)
    favicon = EmbeddedDocumentField(ImageTemplate)