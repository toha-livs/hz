users = {
    'fields': {
        'name': str,
        'email': str,
        'password': str,
        'last_login': int,
        'is_active': bool,
        'image': str,
        'tel': str
    },
    'temp_fields': [
        'groups'
    ],
    'filters': {
        'groups': 'filter_groups'
    },
    'unique_fields': (
        'email',
        'tel'
    )

}

users_tokens = {
    'fields': {
        'name': str,
        'symbol': str,
        'code': str,
        'rate': int,
        'rates': list,
        'last_update': int,
    },
}

groups = {
    'fields': {
        'users': list,
        'name': str,
        'permissions': list,
        'g_type': str,
        'is_owner': bool,
        'project': str
    },
    'temp_fields': [
        'users'
    ],
    'filters': {
        'users': 'filter_users'
    }
}
groups_templates = {
    'fields': {
        'name': str,
        'permissions': list,
        'g_type': str,
    },
}

projects = {
    'unique_fields': [
        'domain'
    ],
    'fields': {
        'name': str,
        'domain': str,
        'additional_domains': list,
        'address': list,
        'logo': object,
        'favicon': object
    },
}

currencies = {
    'fields': {
        'name': str,
        'symbol': str,
        'code': str,
        'rate': int,
        'rates': list,
        'last_update': int,
    },
    'unique_fields': (
        'code',
    )

}

countries = {
    'fields': {
        'name': str,
        'iso2': str,
        'dial_code': str,
        'priority': int,
        'area_codes': list,
        'currency': str,
    },
    'unique_fields': (
        'iso2',
    )
}

cities = {
    'fields': {
        'name': str,
        'country_code': str,
        'default': bool,
        'active': str,
        'lat': int,
        'lng': int,
        'language': object,
        'number_phone': str,
        'exist_store': bool

    }
}

sms = {
    'fields': {
        'tel': str,
        'code': str,
        'created': float,
        'expire': float
    },

}
