from falcon_core.routes import route
from .resources import UsersManage

routes = [
    route('/', UsersManage()),
]
