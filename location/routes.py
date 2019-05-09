from falcon_core.routes import route, include

routes = [
    route('/countries', include('location.country.routes')),
    route('/currencies', include('location.currency.routes')),
    route('/cities', include('location.city.routes')),
]
