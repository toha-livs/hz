from falcon_core.routes import route, include

routes = [
    route('/users/', include("auth.user.routes")),
    route('/groups/', include("auth.group.routes")),
    route('/projects/', include("auth.project.routes"))
]
