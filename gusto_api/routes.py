from mongoengine import QuerySet

from falcon_core.routes import route, include
from falcon_core.utils import DictGenerator, register_iterable

register_iterable(DictGenerator, QuerySet)

routes = [
    route('/', include('auth.routes')),
]
