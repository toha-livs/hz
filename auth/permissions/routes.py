from falcon_core.routes import route
from .resources import PermissionsResource

routes = [
    route('', PermissionsResource())
]
