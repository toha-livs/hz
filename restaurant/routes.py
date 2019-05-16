from falcon_core.routes import route
from .resources import WorkingTimeResource

routes = [
    route('/workingtime', WorkingTimeResource())
]
