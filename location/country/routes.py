from falcon_core.routes import route

from location.currency.resources import CurrenciesResource, CurrencyResource

routes = [
    route('/', CurrenciesResource()),
    route('/{id}/', CurrencyResource()),
]
