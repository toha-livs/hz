
from falcon_core.routes import route, include


routes = [
    route('/location/', include('location.routes')),
    route('/', include("auth.routes")),
]

