from falcon_core.routes import route, include

routes = [
    route('/users/', include('auth.users.routes')),
]
