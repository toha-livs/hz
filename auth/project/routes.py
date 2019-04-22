from falcon_core.routes import route
from .resources import ProjectResource

routes = [
    route('/', ProjectResource()),
    route('/{id}/', ProjectResource()),
    route('/groups/{group_id}/', ProjectResource()),
]
