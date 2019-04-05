from falcon_core.routes import route
from .resources import LoginResource

routes = [
    route('/login/', LoginResource())
]
