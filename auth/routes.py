from falcon_core.routes import route
from .resources import GroupsResource

routes = [
    route('/', GroupsResource())
]
