from falcon_core.routes import route

from .resources import UsersResource, UserResource,LoginResource

routes = [
    route('/', UsersResource()),
    route('/login/', LoginResource()),
    # route('/registration/', )
    route('/{id}/', UserResource()),
]
