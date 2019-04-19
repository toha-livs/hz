from falcon_core.routes import route

from auth.users.resources import UsersLoginResource

routes = [
    route('/login/', UsersLoginResource()),
]
