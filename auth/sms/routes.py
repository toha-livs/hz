from falcon_core.routes import route
from .resources import SMSResource,SMSCheckResource

routes = [
    route('',SMSResource()),
    route('/check',SMSCheckResource())
]
