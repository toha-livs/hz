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
    ),
    'response_templates':
        {'login': (
            ('id', 'string'),
            ('name', 'string'),
            ('email', 'string'),
            ('tel', 'string'),
            ('is_active', 'boolean'),
            ('get_date_created:date_created', 'integer'),
            ('image', 'string'),
            ('token:token', 'string'),
            ('groups', 'objects', (
                ('id', 'string'),
                ('name', 'string'),
                ('project', 'object', (
                    ('id', 'string'),
                    ('name', 'object', (
                        ('en', 'string'),
                        ('ru', 'string'),
                        ('uk', 'string'),
                    ))
                )),
                ('permissions', 'objects', (
                    ('id', 'string'),
                    ('get_access:access', 'string'),
                )),
                ('g_type', 'string'),
                ('is_owner', 'boolean')
            ))
        ),
            'short': (
                ('id', 'string'),
                ('name', 'string'),
                ('email', 'string'),
                ('tel', 'string'),
                ('is_active', 'boolean'),
                ('get_date_created:date_created', 'integer'),
                ('image', 'string'),
                ('groups', 'objects', (
                    ('id', 'string'),
                    ('name', 'string'),
                    ('project', 'object', (
                        ('id', 'string'),
                        ('name', 'object', (
                            ('en', 'string'),
                            ('ru', 'string'),
                            ('uk', 'string'),
                        ))
                    )),
                    ('permissions', 'objects', (
                        ('id', 'string'),
                        ('get_access:access', 'string'),
                    )),
                    ('g_type', 'string'),
                    ('is_owner', 'boolean')
                ))
            )
        }

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
    },
    'response_templates': {
        'short': (
            ('id', 'string'),
            ('name', 'string'),
            ('g_type', 'string'),
            ('is_owner', 'boolean'),
            ('project', 'object', (
                ('id', 'string'),
                ('name', 'object', (
                    ('en', 'string'),
                    ('ru', 'string'),
                    ('uk', 'string'),
                )),
                ('additional_domains', 'list'),

            )),
            ('permissions', 'objects', (
                ('id', 'string'),
                ('get_access:access', 'string')
            )),
        ),
        'long': (
            ('id', 'string'),
            ('name', 'string'),
            ('g_type', 'string'),
            ('is_owner', 'boolean'),
            ('users', 'objects', (
                ('name', 'string'),
                ('email', 'string'),
                ('is_active', 'boolean'),
                ('image', 'string'),
            )),
            ('project', 'object', (
                ('id', 'string'),
                ('name', 'object', (
                    ('en', 'string'),
                    ('ru', 'string'),
                    ('uk', 'string'),
                )),

            )),
            ('permissions', 'objects', (
                ('id', 'string'),
                ('get_access:access', 'string')
            )),
        )
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
    'response_templates': {
        'short':
            (
                ('id', 'string'),
                ('domain', 'string'),
                ('additional_domains', 'list'),
                ('address', 'objects', (
                    ('en', 'string'),
                    ('ru', 'string'),
                    ('uk', 'string'),
                )),
                ('logo', 'string'),
                ('favicon', 'string'),
                ('name', 'object', (
                    ('en', 'string'),
                    ('ru', 'string'),
                    ('uk', 'string'),
                )),
            )
    }
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
    'response_template': {
        'short': (
            ('id', 'string'),
            ('name', 'string'),
            ('symbol', 'string'),
            ('code', 'string'),
            ('rate', 'integer'),
            ('rates', 'list'),
            ('get_last_update:last_update', 'float')
        )
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
    'response_template': {
        'short': (
            ('id', 'string'),
            ('name', 'string'),
            ('iso2', 'string'),
            ('dial_code', 'string'),
            ('priority', 'integer'),
            ('area_codes', 'list'),
            ('currency', 'object', (
                ('name', 'string'),
                ('symbol', 'string'),
                ('code', 'string'),
                ('rate', 'integer'),
                ('rate', 'integer')
            )),
        ),
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

    },
    'response_templates': {
        'short': (
            ('name', 'string'),
            ('country_code', 'string'),
            ('default', 'boolean'),
            ('active', 'boolean'),
            ('lat', 'integer'),
            ('lng', 'integer'),
            ('number_phone', 'string'),
            ('language', 'object', (
                ('en', 'string'),
                ('ru', 'string'),
                ('uk', 'string'),
            ),),
            ('exist_store', 'boolean'),
        )
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
