import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '5d8c8889b597776c1759c35440e7ddf5980d813b75e02d18e4244223e014326b'

DEBUG = True

ALLOWED_HOSTS = ['localhost']

MIDDLEWARE = []

INSTALLED_APPS = [
    'falcon_core',
]

DATABASES = {}

ROUTER_CONVERTERS = {}

ROUTES = 'gusto_api.routes'

DEPLOY = {}
