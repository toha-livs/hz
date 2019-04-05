from falcon_core.routes import route
from .resources import GroupsResource, GroupResource

routes = [
    route('/', GroupsResource()),
    route('/{id}/', GroupResource()),
    route('/projects/{project_id}/', GroupResource()),
]
