from falcon_core.routes import route, include

routes = [
    route('/', include('auth.routes')),
]
