from falcon_core.routes import route

from auth.users.resources import UsersLoginResource, UsersResource

routes = [
    route('/', UsersResource()),
    route('/{id}/', UsersResource()),
    route('/login/', UsersLoginResource()),
]
