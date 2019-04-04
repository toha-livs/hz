from falcon_core.routes import route
from .resources import UsersResource

routes = [
    route('/', UsersResource()),
]
