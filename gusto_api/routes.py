from falcon_core.routes import route, include


routes = [
    route('/groups/', include("auth.routes")),
]
