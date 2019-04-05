from falcon_core.routes import route
from .resources import UsersResource, UserResource

routes = [
    route('/', UsersResource()),
    route('/{user_id}/', UserResource()),
]
