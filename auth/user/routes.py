from falcon_core.routes import route

from .resources import UsersResource, UserResource, LoginResource, RegistrationResource

routes = [
    route('', UsersResource()),
    route('/login', LoginResource()),
    route('/registration', RegistrationResource()),
    route('/{id}', UserResource()),
]
