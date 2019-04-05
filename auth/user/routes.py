from falcon_core.routes import route
from .resources import LoginResource
from .resources import UsersResource, UserResource

routes = [
    route('/', UsersResource()),
    route('/login/', LoginResource()),
    route('/{user_id}/', UserResource()),
]
