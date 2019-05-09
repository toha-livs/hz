from falcon_core.routes import route
from .resources import CitiesResource, CityResource

routes = [
    route('', CitiesResource()),
    route('/{id}', CityResource()),
]
