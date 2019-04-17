from falcon_core.routes import route, include

routes = [
    route('/cities/', include('location.city.routes')),
]
