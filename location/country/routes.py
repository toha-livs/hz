from falcon_core.routes import route

from location.country.resources import CountriesResource, CountryResource

routes = [
    route('/', CountriesResource()),
    route('/{id}/', CountryResource()),
]
