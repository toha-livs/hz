from falcon_core.routes import route

from location.currency.resources import CurrencyResource, CurrenciesResource

routes = [
    route('/', CurrenciesResource()),
    route('/{id}/', CurrencyResource()),
]
